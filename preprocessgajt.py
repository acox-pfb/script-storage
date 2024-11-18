import sys
import re
from pathlib import Path
import binascii
import zlib

def PrintUsage():
    print("preprocessgajt.py - Usage:")
    print("preprocessgajt.py <Log File> <TimeOffset>")
    print("preprocessgajt.py will write the new file out appended with _WITH-TIME.DAT")
    print("A SUM file will be output as well with failed CRCs and missing sequence numbers")


numArgs = len(sys.argv)
if numArgs != 3:
    PrintUsage()

inputFile = open(sys.argv[1])
delimiters = ",;*\r\n/s"

outFile= open((Path(sys.argv[1]).stem) + "_WITH-TIME.DAT", "w")
outFileSummary= open((Path(sys.argv[1]).stem) + "_WITH-TIME.SUM", "w")

# Variables for the loop
bReadFirstTime = False
startTime = int(sys.argv[2])
startHeaderTime = 0
headerTime = 0
newTimeStamp = startTime
expectedMsgSequence = 0
line = ""
bCompleteMessage = False
totalLinesRead = 0
totalLinesWritten = 0
totalCRCGood = 0
totalCRCBad = 0
msgCountDict = dict()
sequenceJump = 0
bSequenceJumped = False

# Loop through, this is expecting only strings and parsing per line
for row in inputFile:
    totalLinesRead += 1
    # Sanity checking the row, we remove any replies and wait for a complete message.
    # Current assumption for a complete line is the '*' with CRC at the end. 
    # If this does not exist then the line is appended and looped until we have it. 
    if len(row) == 0:
        continue
    if row.find("<OK") != -1 :
        continue
    
    if row.find("<") != -1:
        continue
    
    if (row.find("*") == -1):
        line += row[0:len(row)]
    else:
        bCompleteMessage = True

    if bCompleteMessage == False:
        continue

    line += row   

    # We have the line, now remove the leading # and the * + CRC so we can check the CRC.
    # If CRC fails we note it in the SUM file and do not pass it to the output file
    if line[0] != '#':
        line = line[line.find('#'):-1]

    message = line[1:line.find("*")]
    messageBytes = bytes(message, 'utf-8')
    crc = 0xFFFFFFFF ^ binascii.crc32(messageBytes, 0xFFFFFFFF)
    crcString = f'{crc:08X}'
 
    # Replace any \r and \n found in the message
    # This is only here because of SITREP3
    message = message.replace("\n", "")
    message = message.replace("\r", "")

    # We start the fixing here
    messageParts = str.split(message, ';')
    if len(messageParts) != 2:
        outFileSummary.write("Splitting header and message on ';' resulted in to many fields " + str(len(messageParts)) + ": " + line)
        line = ""
        bCompleteMessage = False
        continue

    headerFields = re.split("[\s,;]+", messageParts[0])
    messageFields = re.split("[\s,;*]+", messageParts[1])
    # Get the CRC in the message and compare
    msgCRC = line[line.find("*")+1:].replace("\n", "")
    
  


    if msgCRC != crcString:
        outFileSummary.write("CRC Mismatch on " + headerFields[0] + " Expected: " + crcString + " Found: " + msgCRC + "\r\n")
        print("CRC Mismatch on " + headerFields[0] + " Expected: " + crcString + " Found: " + msgCRC + "\n")
        totalCRCBad += 1
        line = ""
        bCompleteMessage = False
        continue
    else:
        totalCRCGood += 1

    if len(headerFields) != 8:
        outFileSummary.write("Header does not have expected number of fields. Expected 8, Parsed: " + str(len(headerFields)) + " For: " + headerFields[0] + "\n")
        print("Header does not have expected number of fields. Expected 8, Parsed: " + str(len(headerFields)) + " For: " + headerFields[0])
        line = ""
        bCompleteMessage = False
        continue


    # Get the time status field
    timeStatus = int(headerFields[5])

    # If this is our first pass, we need to get the header time (as a just in case)
    # As well as the first sequence for sequence checking.
    if bReadFirstTime == False:
        startHeaderTime = headerTime = int(headerFields[7]) / 1000
        startHeaderTime = round(startHeaderTime)
        expectedMsgSequence = int (headerFields[1])
        bReadFirstTime = True
    else:
        expectedMsgSequence += 1

        # Handle overflow of msg sequence
        if expectedMsgSequence == 65536:
            expectedMsgSequence = 0

        sequenceNumber = int(headerFields[1])
        print("Sequence:" + headerFields[1])
        if sequenceNumber != expectedMsgSequence:
            bSequenceJumped = True
            #check on the jump, if it's 
            if expectedMsgSequence < sequenceNumber:
                sequenceJump =  sequenceNumber - expectedMsgSequence               
            else:
                #it's possible there was a roll over
                sequenceJump = sequenceNumber + (65535 - expectedMsgSequence)
            
            outFileSummary.write("Msg Sequence error: Expected: " + str(expectedMsgSequence) + " Read: " + str(sequenceNumber) + "Total Jump: " + str(sequenceJump) + "\n")
            print("Msg Sequence error: Expected: " + str(expectedMsgSequence) + " Read: " + str(sequenceNumber) + "Total Jump: " + str(sequenceJump) + "\n")
                    
            
            expectedMsgSequence = int(headerFields[1])
         
    if headerFields[0] not in msgCountDict:
        msgCountDict[headerFields[0]] = 1
    else:
        msgCountDict[headerFields[0]] += 1

    #time status is set, then we can just replace the time since running with realtime.
    if(timeStatus == 1):
        newTimeStamp = (int(headerFields[7]) / 1000 - startHeaderTime) + startTime

    
    # This covers the AE and 410 which do not put a time since running in the timestamp
    # This bandaid is to key off SITREP since we know this will be asked for at 1Hz.
    if(timeStatus == 0):
        headerFields[6] = "1"
        if("SITREP2A" in headerFields[0]):
            if bSequenceJumped == False:
                newTimeStamp = newTimeStamp + 1
            else:
                oldTimeStamp = newTimeStamp
                newTimeStamp = newTimeStamp + round(sequenceJump / 3)
                bSequenceJumped = False
                outFileSummary.write("Recomputed timestamp based on jump: Old: " + str(oldTimeStamp) + " New: " + str(newTimeStamp) + "Sequence Jump: " + str(sequenceJump/ 3) + "\n")
                print("Recomputed timestamp based on jump: Old: " + str(oldTimeStamp) + " New: " + str(newTimeStamp) + "Sequence Jump: " + str(sequenceJump/ 3) + "\n")

    
    headerFields[7] = f'{(newTimeStamp*1000):.0f}'

    #reassemble the header
    newHeader = headerFields[0]
    for i in range(len(headerFields)):
        if i == 0:
            continue
        
        newHeader += "," + headerFields[i]

   
    newMessageBody = messageFields[0]
    for i in range(len(messageFields)):
      if i == 0:
          continue
      newMessageBody += "," + messageFields[i]

    correctedMessage = newHeader[0:len(newHeader)] + ";" + newMessageBody
    newCRC = (0xFFFFFFFF ^ binascii.crc32(bytes(correctedMessage, 'utf-8'), 0xFFFFFFFF))
    newMessage = "#" + correctedMessage + '*' + f'{newCRC:X}'
    outFile.write(newMessage + "\r")
    totalLinesWritten += 1
    line = ""
    bCompleteMessage = False

outFileSummary.write("Summary: \n")
outFileSummary.write("Total Lines Read: " + str(totalLinesRead) + "\n")
outFileSummary.write("Total Lines Written: " + str(totalLinesWritten) + "\n")
outFileSummary.write("Total Lines Written: " + str(totalLinesWritten) + "\n")
outFileSummary.write("Total CRC Good: " + str(totalCRCGood) + "\n")
outFileSummary.write("Total CRC Bad: " + str(totalCRCBad) + "\n")

outFileSummary.write("\n\nLogs Found:\n")

totalLogCount = 0
for msg in msgCountDict:
    outFileSummary.write(msg + "\t" + str(msgCountDict[msg]) + "\n")
    totalLogCount += msgCountDict[msg]


outFileSummary.write("\nTotal Log Count: " + str(totalLogCount) + "\n")


outFile.close()
outFileSummary.close()
