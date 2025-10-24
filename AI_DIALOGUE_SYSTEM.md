# 🤖 AI-Powered Personalized Dialogue System

## Overview
The 3D Python learning game now uses **Gemini AI** to generate dynamic, personalized conversations that adapt to each student's input. The characters (Alex and Sam) speak naturally using the student's name and respond intelligently to what they type.

## Key Features

### 1. **Personalized with Student Name** 👤
- **Automatic**: If logged in, fetches name from Flask session (database)
- **Manual**: Student can enter their name at the start
- **Fallback**: Uses "Student" if no name provided
- Characters use the student's name throughout: "Hello Dhanush!" instead of generic greetings

### 2. **AI-Generated Responses** 🧠
The system uses Gemini AI to create natural, context-aware dialogue at 5 key stages:

#### Stage 1: Greeting
- **Trigger**: Game starts
- **AI Role**: Sam responds to Alex's greeting
- **Example**: "Hello Dhanush! I'm doing great!" (varies each time)

#### Stage 2: String Response
- **Trigger**: Student successfully prints their first string
- **AI Role**: Sam acknowledges what the student made them say
- **Example Input**: Student types `print("Hey there!")`
- **AI Response**: "Thanks Dhanush! That worked perfectly!"
- **If Creative**: "Haha! That's creative Dhanush!"

#### Stage 3: Age Question
- **Trigger**: After successful string print
- **AI Role**: Alex asks the student about their age
- **Example**: "Nice! Dhanush, how old are you?"
- **Varies**: "Cool! What's your age Dhanush?"

#### Stage 4: Age Response
- **Trigger**: Student successfully prints a number
- **AI Role**: Sam confirms their age
- **Example Input**: Student types `print(20)`
- **AI Response**: "I'm 20 years old!" or "Yes! I'm 20!"

#### Stage 5: Celebration
- **Trigger**: Both challenges completed
- **AI Role**: Alex celebrates the student's success
- **Example**: "Awesome Dhanush! You're a Python star!"

### 3. **Stays On Topic** 🎯
- AI is constrained by system prompts to stay focused on teaching Python `print()`
- Responses are kept short (8-12 words max)
- Never goes off-topic into unrelated subjects

### 4. **Intelligent Error Handling** 💡
- If student types partial code: "Dhanush, add quotes! 🤔"
- If student forgets quotes for strings: Gemini generates a helpful hint
- If student adds quotes to numbers: "Dhanush, no quotes for numbers! 🔢"

## How It Works

### Backend (Flask - `app.py`)

```python
@app.route('/api/dialogue', methods=['POST'])
def ai_dialogue():
    # Receives:
    # - student_name: "Dhanush"
    # - stage: "greeting", "string_response", etc.
    # - user_input: What the student typed
    # - challenge: 1 or 2
    
    # Gemini generates contextual response
    # Returns: { "dialogue": "Hello Dhanush! I'm doing great!" }
```

### Frontend (`python_hello_world_3d.html`)

```javascript
// 1. Fetch student name from session or input
let studentName = await fetchStudentName(); // "Dhanush"

// 2. When student succeeds, get AI response
const samResponse = await getAIDialogue('string_response', userText);
// Returns: "Thanks Dhanush! That worked!"

// 3. Display in speech bubble and speak it
samSpeech.textContent = samResponse + ' 😊';
speak(samResponse, 1);
```

## API Endpoints

### `/api/user-info` (GET)
- Fetches logged-in student's name from database
- Returns: `{ "name": "Dhanush" }` or `{ "name": null }`

### `/api/dialogue` (POST)
- Generates personalized AI dialogue
- **Request Body**:
  ```json
  {
    "student_name": "Dhanush",
    "stage": "string_response",
    "user_input": "Hey there!",
    "challenge": 1
  }
  ```
- **Response**:
  ```json
  {
    "dialogue": "Thanks Dhanush! That worked!",
    "should_continue": true
  }
  ```

## Example Flow (Student: "Dhanush")

1. **Game Starts**:
   - Alex: "Hello Sam! How are you? 👋"
   - Sam: "..." (waiting)
   - Alex: "**Dhanush**, help Sam greet back!"

2. **Student Types**: `print("Hi Sam!")`
   - Sam: "Hi Sam! 😊" (speaks what student typed)
   - *AI generates*: "Thanks **Dhanush**! That worked great!"
   - Sam: "Thanks **Dhanush**! That worked great! 😊"

3. **Alex Asks** (AI-generated):
   - Alex: "Nice! **Dhanush**, how old are you?"

4. **Student Types**: `print(20)`
   - Sam: "I'm 20 years old! 🎊" (AI-generated)
   - Alex: "Awesome **Dhanush**! You're a Python star!" (AI-generated)

## Benefits

### ✅ Personalized Learning
- Students feel recognized and engaged
- Uses their actual name throughout

### ✅ Natural Conversation
- Not scripted - AI generates fresh responses
- Acknowledges creative student input
- Feels like talking to real characters

### ✅ Stays Educational
- AI constrained to Python teaching context
- Never goes off-topic
- Reinforces learning objectives

### ✅ Flexible Validation
- Student can type ANY greeting - "Hi!", "Hello!", "Hey there!"
- Student can type ANY age - 15, 20, 18, etc.
- Not restricted to exact text matching

### ✅ Secure
- API key stored on backend only
- All AI calls go through Flask proxy
- No exposure to frontend

## Configuration

### Required Environment Variable
```bash
GEMINI_API_KEY=AIzaSyC_TRi_uYXTSXfmOk8u5hmW1J2aKGKgHWg
```

### Fallback Behavior
If Gemini API is unavailable:
- System uses default responses
- Still uses student's name
- Game continues working normally

## Testing

### Manual Testing
1. Start Flask: `python app.py`
2. Open `python_hello_world_3d.html` in Live Server
3. Enter your name: "Dhanush"
4. Click "Start!"
5. Observe personalized dialogue using your name
6. Try different inputs to see AI adapt

### With User Session
1. Log in to the platform
2. Navigate to the lesson with 3D game
3. System automatically uses your registered name
4. No need to enter name again

## Future Enhancements

1. **Multi-language Support**: Gemini can generate dialogue in student's preferred language
2. **Difficulty Adaptation**: AI adjusts complexity based on student's performance
3. **More Interactions**: Expand to other Python concepts (variables, loops, etc.)
4. **Voice Recognition**: Student speaks instead of typing
5. **Emotion Detection**: AI responds to student's mood/frustration level

## Technical Notes

- **AI Model**: Gemini 1.5 Flash (fast, cost-effective)
- **Response Time**: ~1-2 seconds per AI call
- **Token Limit**: Prompts kept short to minimize cost
- **Safety**: System prompts constrain AI behavior
- **Error Handling**: Graceful fallbacks at every stage

---

**Created**: October 23, 2025  
**Author**: AI Assistant  
**For**: Luminex Learning Platform - Dhanush

