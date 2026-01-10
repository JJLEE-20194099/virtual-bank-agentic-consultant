Virtual Bank Agentic Consultant (VBAC)

#Prototype1
+ Analyze conversation btw customer and bank
+ Client DB, Bank info, ...
+ Suggestion, ...

## Step 1
+ Audio flow  
   speak
 → 100ms PCM
 → WebSocket
 → gRPC
 → ASR
 → transcript
 → UI (≈300–400ms)
