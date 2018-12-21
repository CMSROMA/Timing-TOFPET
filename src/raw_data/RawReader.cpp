#include <shm_raw.hpp>
#include "RawReader.hpp"

#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <assert.h>

using namespace std;
using namespace PETSYS;

static const unsigned dataFileBufferSize = 131072; // 128K
RawReader::RawReader() :
        steps(vector<Step>()),
	dataFile(-1)

{
	assert(dataFileBufferSize >= MaxRawDataFrameSize * sizeof(uint64_t));
	dataFileBuffer = new char[dataFileBufferSize];
	dataFileBufferPtr = dataFileBuffer;
	dataFileBufferEnd = dataFileBuffer;
}

RawReader::~RawReader()
{
	delete [] dataFileBuffer;
	close(dataFile);
}

RawReader *RawReader::openFile(const char *fnPrefix)
{
	char fName[1024];
	sprintf(fName, "%s.idxf", fnPrefix);
	FILE *idxFile = fopen(fName, "r");
	if(idxFile == NULL)  {
		fprintf(stderr, "Could not open '%s' for reading: %s\n", fName, strerror(errno));
                exit(1);
	}

	sprintf(fName, "%s.rawf", fnPrefix);
	int rawFile = open(fName, O_RDONLY);
	if(rawFile == -1) {
		fprintf(stderr, "Could not open '%s' for reading: %s\n", fName, strerror(errno));
                exit(1);
	}

	uint64_t header[8];
	ssize_t r = read(rawFile, (void *)header, sizeof(uint64_t)*8);
	if(r < 1) {
		fprintf(stderr, "Could not read from '%s'\n", fName, strerror(errno));
		exit(1);
	}
	else if (r < sizeof(uint64_t)*8) {
		fprintf(stderr, "Read only %d bytes from '%s', expected %d\n", r, fName, sizeof(uint64_t)*8);
		exit(1);
	}

	RawReader *reader = new RawReader();
	reader->dataFile = rawFile;
	reader->frequency = header[0] & 0xFFFFFFFFUL;
	reader->qdcMode = (header[0] & 0x100000000UL) != 0;

	Step step;
	while(fscanf(idxFile, "%lu\t%lu\t%lld\t%lld\t%f\t%f", &step.stepBegin, &step.stepEnd, &step.stepFirstFrame, &step.stepLastFrame, &step.step1, &step.step2) == 6) {
		reader->steps.push_back(step);
	}
	return reader;
}

int RawReader::getNSteps()
{
	return steps.size();
}

double RawReader::getFrequency()
{
	return (double) frequency;
}

bool RawReader::isQDC()
{
	return qdcMode;
}

void RawReader::getStepValue(int n, float &step1, float &step2)
{
	Step step = steps[n];
	step1 = step.step1;
	step2 = step.step2;
}

int RawReader::readFromDataFile(char *buf, int count)
{
	int rval = 0;
	while(rval < count) {
		// Read from file if needed
		if(dataFileBufferPtr == dataFileBufferEnd) {
			int r = read(dataFile, dataFileBuffer, dataFileBufferSize);
			// We should be able to read at least 1 byte here
			assert(r >= 1);
			dataFileBufferPtr = dataFileBuffer;
			dataFileBufferEnd = dataFileBuffer + r;

			off_t current = lseek(dataFile, 0, SEEK_CUR);
			readahead(dataFile, current, dataFileBufferSize);
		}

		int countRemaining = count - rval;
		int bufferRemaining = dataFileBufferEnd - dataFileBufferPtr;
		int count2 = (countRemaining < bufferRemaining) ? countRemaining : bufferRemaining;

		memcpy(buf, dataFileBufferPtr, count2);
		dataFileBufferPtr += count2;
		buf += count2;
		rval += count2;
	};
	return rval;
}

void RawReader::processStep(int n, bool verbose, EventSink<RawHit> *sink)
{
	Step step = steps[n];
	
	sink->pushT0(0);
	
	RawDataFrame *dataFrame = new RawDataFrame;
	EventBuffer<RawHit> *outBuffer = NULL; 
	const long outBlockSize = 4*1024;
	long long currentBufferFirstFrame = 0;
	
	long long lastFrameID = -1;
	bool lastFrameWasLost0 = false;
	long long nFrameLost0 = 0;
	long long nFrameLostN = 0;
	long long nEventsNoLost = 0;
	long long nEventsSomeLost = 0;
	
	// Set file handle to start of step
	lseek(dataFile, step.stepBegin, SEEK_SET);
	off_t currentPosition = step.stepBegin;
	// Reset file buffer pointers
	dataFileBufferPtr = dataFileBuffer;
	dataFileBufferEnd = dataFileBuffer;
	while (currentPosition < step.stepEnd) {
		int r;
		// Read frame header
		r = readFromDataFile((char*)((dataFrame->data)+0), 2*sizeof(uint64_t));
		assert(r == 2*sizeof(uint64_t));
		currentPosition += r;
		
		int N = dataFrame->getNEvents();
		if(N == 0) continue;

		assert((N+2) < MaxRawDataFrameSize);

		r = readFromDataFile((char*)((dataFrame->data)+2), N*sizeof(uint64_t));
		assert(r == N*sizeof(uint64_t));
		currentPosition += r;
		
		
		if(outBuffer == NULL) {
			currentBufferFirstFrame = dataFrame->getFrameID();
			outBuffer = new EventBuffer<RawHit>(outBlockSize, currentBufferFirstFrame * 1024);
			
		}
		else if(outBuffer->getSize() + N > outBlockSize) {
			sink->pushEvents(outBuffer);
			currentBufferFirstFrame = dataFrame->getFrameID();
			outBuffer = new EventBuffer<RawHit>(outBlockSize, currentBufferFirstFrame * 1024);
		}
		
		long long frameID = dataFrame->getFrameID();
		bool frameLost = dataFrame->getFrameLost();
		
		// Account skipped frames with all events lost
		if (frameID != lastFrameID + 1) {
			// We have skipped frames...
			if(lastFrameWasLost0) {
				// ... and they indicate lost frames
				nFrameLost0 += (frameID - lastFrameID) - 1;
			}
		}
		
		// Account frames with lost data
		if(frameLost && N == 0) nFrameLost0 += 1;
		if(frameLost && N != 0) nFrameLostN += 1;
		
		if(frameLost) 
			nEventsSomeLost += N;
		else
			nEventsNoLost += N;
		
		// Keep track of frame with all event lost
		lastFrameWasLost0 = (frameLost && N == 0);
		lastFrameID = frameID;
		
		for(int i = 0; i < N; i++) {
			RawHit &e = outBuffer->getWriteSlot();
			
			e.channelID = dataFrame->getChannelID(i);
			e.tacID = dataFrame->getTacID(i);
			e.frameID = frameID;
			e.tcoarse = dataFrame->getTCoarse(i);
			e.tfine = dataFrame->getTFine(i);
			e.ecoarse = dataFrame->getECoarse(i);
			e.efine = dataFrame->getEFine(i);
			
			e.time = (frameID - currentBufferFirstFrame) * 1024 + e.tcoarse;
			e.timeEnd = (frameID - currentBufferFirstFrame) * 1024 + e.ecoarse;
			if((e.timeEnd - e.time) < -256) e.timeEnd += 1024;
			
			e.valid = true;
			
			outBuffer->pushWriteSlot();
		}
		outBuffer->setTMax((frameID + 1) * 1024);
	}
	
	if(outBuffer != NULL) {
		sink->pushEvents(outBuffer);
		outBuffer = NULL;
	}
	
	sink->finish();
	if(verbose) {
		fprintf(stderr, "RawReader report\n");
		fprintf(stderr, "step values: %f %f\n", step.step1, step.step2);
		fprintf(stderr, " data frames\n");
		fprintf(stderr, " %10lld total\n", step.stepLastFrame - step.stepFirstFrame);
		fprintf(stderr, " %10lld (%4.1f%%) were missing all data\n", nFrameLost0, 100.0 * nFrameLost0 / (step.stepLastFrame - step.stepFirstFrame));
		fprintf(stderr, " %10lld (%4.1f%%) were missing some data\n", nFrameLostN, 100.0 * nFrameLost0 / (step.stepLastFrame - step.stepFirstFrame));
		fprintf(stderr, " events frames\n");
		fprintf(stderr, " %10lld total\n", nEventsNoLost + nEventsSomeLost);
		long long goodFrames = step.stepLastFrame - step.stepFirstFrame - nFrameLost0 - nFrameLostN;
		fprintf(stderr, " %10.1f events per frame avergage\n", 1.0 * nEventsNoLost / goodFrames);
		sink->report();
	}

	delete dataFrame;
	delete sink;
	
}
