document.addEventListener('DOMContentLoaded', () => {
    const lessonIframe = document.getElementById('lesson-iframe');
    const quizPrompt = document.getElementById('quizPrompt');
    const quizLink = document.getElementById('quizLink');
    const lessonTitle = document.getElementById('lesson-title');
    
    let currentLessonId = null;
  
    (async function loadLesson() {
      try {
        // 1. Get lesson ID or slug from URL (e.g., lesson.html?id=1 or lesson.html?slug=lesson-title)
        const params = new URLSearchParams(window.location.search);
        const lessonId = params.get('id');
        const lessonSlug = params.get('slug');
        
        if (!lessonId && !lessonSlug) {
          throw new Error('No lesson ID or slug provided.');
        }
        
        // 2. Fetch lesson data from our API
        let response;
        if (lessonId) {
          // Use ID-based endpoint
          response = await apiFetch(`/api/lessons/${lessonId}`);
          currentLessonId = lessonId;
        } else {
          // Use slug-based endpoint
          response = await apiFetch(`/api/lessons/slug/${lessonSlug}`);
          currentLessonId = null; // We'll get the ID from the response
        }
        
        if (!response.ok) {
          throw new Error('Could not load lesson data.');
        }
        
        const lesson = await response.json();
        
        // Set currentLessonId from the response if we used slug
        if (!currentLessonId) {
          currentLessonId = lesson.id;
        }
        
        // Set the lesson title
        lessonTitle.textContent = lesson.title;
        
        // 3. Set the iframe source to the uploaded lesson file
        // lesson.ar_model_url will be "/uploads/for-loop-lesson.html"
        lessonIframe.src = lesson.ar_model_url; 
        
        // Set the quiz link URL
        quizLink.href = `/quiz?lesson_id=${lesson.id}&title=${encodeURIComponent(lesson.title)}&slug=${lesson.slug}`;
  
      } catch (error) {
        console.error(error);
        document.body.innerHTML = `<h1>Error: ${error.message}</h1><a href="/archive">Back to Archive</a>`;
      }
    })();
  
    // 4. Universal lesson completion listener
    window.addEventListener('message', (event) => {
      // Handle both old and new message formats
      const data = event.data;
      
      // New format: { type: 'LESSON_COMPLETE', studentName: '...', timestamp: '...' }
      // Old format: 'lessonComplete'
      const isComplete = (data && data.type === 'LESSON_COMPLETE') || data === 'lessonComplete';
      
      if (isComplete) {
        const studentName = (data && data.studentName) || 'Student';
        console.log(`✅ Lesson completed by ${studentName}!`, data);
        
        // Show beautiful quiz popup
        showQuizPopup(studentName);
      }
    });
    
    // Show quiz popup modal
    function showQuizPopup(studentName) {
      // Create popup if it doesn't exist
      let popup = document.getElementById('universal-quiz-popup');
      
      if (!popup) {
        popup = document.createElement('div');
        popup.id = 'universal-quiz-popup';
        popup.style.cssText = `
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0,0,0,0.85);
          backdrop-filter: blur(5px);
          z-index: 10000;
          display: flex;
          align-items: center;
          justify-content: center;
          animation: fadeIn 0.3s ease;
        `;
        
        popup.innerHTML = `
          <div style="
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 500px;
            width: 90%;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            animation: bounceIn 0.5s ease;
          ">
            <div style="font-size: 60px; margin-bottom: 20px;">🎯</div>
            <h2 style="font-family: 'Fredoka', sans-serif; color: #1E1E2F; font-size: 28px; margin-bottom: 15px;">
              Lesson Complete!
            </h2>
            <p style="color: #5E6C84; font-size: 16px; line-height: 1.6; margin-bottom: 25px;">
              Great job <strong style="color: #00C2FF;">${studentName}</strong>! 
              You've completed this lesson.<br>
              Ready to test your knowledge?
            </p>
            <div style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">
              <button onclick="closeQuizPopup()" style="
                background: #E0E0E0;
                color: #666;
                padding: 14px 28px;
                border: none;
                border-radius: 10px;
                font-family: 'Fredoka', sans-serif;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
              ">
                Skip for Now
              </button>
              <button onclick="goToQuiz()" style="
                background: linear-gradient(135deg, #00C2FF, #667eea);
                color: white;
                padding: 14px 28px;
                border: none;
                border-radius: 10px;
                font-family: 'Fredoka', sans-serif;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(0,194,255,0.4);
                transition: all 0.3s;
              ">
                <i class="fas fa-play"></i> Take Quiz Now
              </button>
            </div>
          </div>
        `;
        
        document.body.appendChild(popup);
      } else {
        // Update student name if popup already exists
        const nameElement = popup.querySelector('strong');
        if (nameElement) {
          nameElement.textContent = studentName;
        }
        popup.style.display = 'flex';
      }
    }
    
    // Close quiz popup
    window.closeQuizPopup = function() {
      const popup = document.getElementById('universal-quiz-popup');
      if (popup) {
        popup.style.display = 'none';
      }
    };
    
    // Go to quiz
    window.goToQuiz = function() {
      if (currentLessonId) {
        window.location.href = quizLink.href;
      } else {
        alert('Quiz link not available');
      }
    };
    
    // Add CSS animations
    if (!document.getElementById('quiz-popup-animations')) {
      const style = document.createElement('style');
      style.id = 'quiz-popup-animations';
      style.textContent = `
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes bounceIn {
          0% { transform: scale(0); opacity: 0; }
          50% { transform: scale(1.05); }
          100% { transform: scale(1); opacity: 1; }
        }
      `;
      document.head.appendChild(style);
    }
  });