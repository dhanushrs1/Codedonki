document.addEventListener('DOMContentLoaded', () => {
    // Get UI elements
    const quizTitle = document.getElementById('quiz-title');
    const loadingMessage = document.getElementById('loading-message');
    const quizContainer = document.getElementById('quiz-container');
    const questionsContainer = document.getElementById('questions-container');
    const submitQuizBtn = document.getElementById('submit-quiz');
    const resultsContainer = document.getElementById('results-container');
    const scoreDisplay = document.getElementById('score-display');
    const xpMessage = document.getElementById('xp-message');
    const aiTipContainer = document.getElementById('ai-tip-container');
    const aiTipText = document.getElementById('ai-tip-text');
    const retryQuizBtn = document.getElementById('retry-quiz');
  
    // 1. Get lesson details from the URL
    const params = new URLSearchParams(window.location.search);
    const lessonId = params.get('lesson_id');
    const lessonTitle = decodeURIComponent(params.get('title') || '');
    const lessonSlug = params.get('slug');
  
    if (!lessonId) {
      document.body.innerHTML = '<h1>Error: Missing lesson details.</h1><a href="/archive">Back to Archive</a>';
      return;
    }
  
    // Set the title of the page
    quizTitle.textContent = `Quiz${lessonTitle ? ` for "${lessonTitle}"` : ''}`;
    
    let quizQuestions = [];
    let userAnswers = {};
    let quizStartTime = null;
    let quizTimerInterval = null;
  
    // 2. Load quiz questions
    (async function loadQuiz() {
      try {
        // Fetch quiz questions
        const response = await apiFetch(`/api/quiz/${lessonId}`);
        
        if (!response.ok) {
          throw new Error('Failed to load quiz questions');
        }
        
        quizQuestions = await response.json();
        
        if (quizQuestions.length === 0) {
          throw new Error('No quiz questions available for this lesson');
        }
        
        // Hide loading and show quiz
        loadingMessage.style.display = 'none';
        quizContainer.style.display = 'block';
        
        // Render questions
        renderQuestions();
        
        // Start timer
        startQuizTimer();
        
      } catch (error) {
        console.error('Quiz loading error:', error);
        loadingMessage.innerHTML = `
          <h3>Error loading quiz</h3>
          <p>${error.message}</p>
          <a href="/archive" class="btn btn-secondary">Back to Lessons</a>
        `;
      }
    })();
    
    function startQuizTimer() {
      quizStartTime = Date.now();
      
      // Create timer display
      const timerDisplay = document.createElement('div');
      timerDisplay.id = 'quiz-timer';
      timerDisplay.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #00C2FF, #667eea);
        color: white;
        padding: 15px 25px;
        border-radius: 12px;
        font-size: 18px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0,194,255,0.3);
        z-index: 1000;
        font-family: 'Fredoka', sans-serif;
      `;
      document.body.appendChild(timerDisplay);
      
      // Update timer every second
      quizTimerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - quizStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        timerDisplay.innerHTML = `⏱️ ${minutes}:${seconds.toString().padStart(2, '0')}`;
      }, 1000);
    }
    
    function stopQuizTimer() {
      if (quizTimerInterval) {
        clearInterval(quizTimerInterval);
        quizTimerInterval = null;
      }
      const timerDisplay = document.getElementById('quiz-timer');
      if (timerDisplay) {
        timerDisplay.remove();
      }
    }
    
    function getTimeElapsed() {
      return Math.floor((Date.now() - quizStartTime) / 1000); // in seconds
    }
    
    function renderQuestions() {
      questionsContainer.innerHTML = '';
      
      quizQuestions.forEach((question, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'question-item';
        questionDiv.innerHTML = `
          <div class="question-text">${index + 1}. ${question.question_text}</div>
          <div class="options-container">
            <label class="option">
              <input type="radio" name="question_${question.id}" value="A">
              <span>A. ${question.option_a}</span>
            </label>
            <label class="option">
              <input type="radio" name="question_${question.id}" value="B">
              <span>B. ${question.option_b}</span>
            </label>
            <label class="option">
              <input type="radio" name="question_${question.id}" value="C">
              <span>C. ${question.option_c}</span>
            </label>
            <label class="option">
              <input type="radio" name="question_${question.id}" value="D">
              <span>D. ${question.option_d}</span>
            </label>
          </div>
        `;
        questionsContainer.appendChild(questionDiv);
      });
      
      // Add event listeners for option selection
      questionsContainer.querySelectorAll('.option').forEach(option => {
        option.addEventListener('click', function() {
          const radio = this.querySelector('input[type="radio"]');
          radio.checked = true;
          
          // Update visual state
          this.parentElement.querySelectorAll('.option').forEach(opt => opt.classList.remove('selected'));
          this.classList.add('selected');
          
          // Store answer
          const questionId = radio.name.split('_')[1];
          userAnswers[questionId] = radio.value;
        });
      });
    }
    
    // Submit quiz
    submitQuizBtn.addEventListener('click', async function() {
      // Check if all questions are answered
      const unanswered = quizQuestions.filter(q => !userAnswers[q.id]);
      if (unanswered.length > 0) {
        showAlert(`Please answer all questions. You have ${unanswered.length} unanswered question(s).`, { type: 'warning' });
        return;
      }
      
      try {
        submitQuizBtn.disabled = true;
        submitQuizBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
        
        // Stop timer and get elapsed time
        stopQuizTimer();
        const timeElapsed = getTimeElapsed();
        
        const response = await apiFetch('/api/quiz/submit', {
          method: 'POST',
          body: JSON.stringify({
            lesson_id: parseInt(lessonId),
            answers: userAnswers,
            time_taken: timeElapsed
          })
        });
        
        const result = await response.json();
        
        // Hide quiz and show results
        quizContainer.style.display = 'none';
        resultsContainer.style.display = 'block';
        
        // Display score
        const scoreClass = result.passed ? 'score-pass' : 'score-fail';
        scoreDisplay.innerHTML = `
          <div class="${scoreClass}">${result.score}%</div>
          <div>${result.passed ? '🎉 Passed!' : '❌ Failed'}</div>
        `;
        
        // Show XP message
        if (result.passed) {
          const minutes = Math.floor(timeElapsed / 60);
          const seconds = timeElapsed % 60;
          const timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;
          
          let xpBreakdown = `<p>🎉 Congratulations! You earned <strong>${result.xp_awarded} XP</strong>!</p>`;
          
          if (result.base_xp && result.time_bonus !== undefined) {
            xpBreakdown += `
              <div style="background: rgba(0,194,255,0.1); padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p style="margin: 5px 0;"><strong>XP Breakdown:</strong></p>
                <p style="margin: 5px 0;">📚 Base XP: ${result.base_xp}</p>
                <p style="margin: 5px 0;">⚡ Time Bonus: ${result.time_bonus > 0 ? '+' : ''}${result.time_bonus} (${timeStr})</p>
                <p style="margin: 5px 0; font-weight: 600; color: #00C2FF;">💫 Total: ${result.xp_awarded} XP</p>
              </div>
            `;
          }
          
          xpMessage.innerHTML = `
            ${xpBreakdown}
            <p>Your new total XP: <strong>${result.new_total_xp}</strong></p>
            ${result.new_badges && result.new_badges.length > 0 ? 
              `<p>🏆 New badges earned: ${result.new_badges.map(b => b.name).join(', ')}</p>` : ''
            }
          `;
        } else {
          xpMessage.innerHTML = `
            <p>You scored ${result.score}%. You need at least 70% to pass.</p>
            <p>${result.retry_message || 'You can retry the quiz.'}</p>
          `;
          retryQuizBtn.style.display = 'inline-flex';
        }
        
        // Get AI tip
        try {
          const aiResponse = await apiFetch('/api/ai-suggestion', {
            method: 'POST',
            body: JSON.stringify({ title: lessonTitle })
          });
          const aiData = await aiResponse.json();
          aiTipText.textContent = aiData.suggestion || "Great job! Keep practicing!";
          aiTipContainer.style.display = 'block';
        } catch (error) {
          console.log('Could not load AI tip');
        }
        
      } catch (error) {
        console.error('Quiz submission error:', error);
        showAlert('Error submitting quiz. Please try again.', { type: 'error' });
        submitQuizBtn.disabled = false;
        submitQuizBtn.innerHTML = 'Submit Quiz <i class="fas fa-paper-plane"></i>';
      }
    });
    
    // Retry quiz
    retryQuizBtn.addEventListener('click', function() {
      userAnswers = {};
      resultsContainer.style.display = 'none';
      quizContainer.style.display = 'block';
      questionsContainer.querySelectorAll('input[type="radio"]').forEach(radio => radio.checked = false);
      questionsContainer.querySelectorAll('.option').forEach(option => option.classList.remove('selected'));
    });
  });