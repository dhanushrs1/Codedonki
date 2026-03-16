// The base URL of our Python server
const API_BASE_URL = 'http://127.0.0.1:5000';

// Get elements from the DOM
const signupForm = document.getElementById('signupForm');
const loginForm = document.getElementById('loginForm');
const errorMessage = document.getElementById('error-message');

// Tab functionality
const tabButtons = document.querySelectorAll('.tab-btn');
const authForms = document.querySelectorAll('.auth-form');

/**
 * Displays an error message on the form.
 * @param {string} message The error message to display.
 */
function displayError(message) {
  if (errorMessage) {
    errorMessage.textContent = message;
    errorMessage.style.display = message ? 'block' : 'none';
  }
}

/**
 * Switch between login and signup tabs
 */
function switchTab(tabName) {
  // Remove active class from all tabs and forms
  tabButtons.forEach(btn => btn.classList.remove('active'));
  authForms.forEach(form => form.classList.remove('active'));
  
  // Add active class to selected tab and form
  document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
  document.getElementById(`${tabName}Form`).classList.add('active');
  
  // Clear any error messages
  displayError('');
}

/**
 * Toggle password visibility
 */
function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  const toggle = input.parentNode.querySelector('.password-toggle i');
  
  if (input.type === 'password') {
    input.type = 'text';
    toggle.classList.remove('fa-eye');
    toggle.classList.add('fa-eye-slash');
  } else {
    input.type = 'password';
    toggle.classList.remove('fa-eye-slash');
    toggle.classList.add('fa-eye');
  }
}

/**
 * Check password strength and return numeric value
 */
function checkPasswordStrengthValue(password) {
  let strength = 0;
  
  if (password.length >= 8) strength++;
  if (password.match(/[a-z]/)) strength++;
  if (password.match(/[A-Z]/)) strength++;
  if (password.match(/[0-9]/)) strength++;
  if (password.match(/[^a-zA-Z0-9]/)) strength++;
  
  return strength;
}

/**
 * Check password strength
 */
function checkPasswordStrength(password) {
  const strengthBar = document.querySelector('.strength-fill');
  const strengthText = document.querySelector('.strength-text');
  
  if (!strengthBar || !strengthText) return;
  
  const strength = checkPasswordStrengthValue(password);
  
  strengthBar.className = 'strength-fill';
  
  if (strength < 2) {
    strengthBar.classList.add('weak');
    strengthText.textContent = 'Weak';
  } else if (strength < 3) {
    strengthBar.classList.add('fair');
    strengthText.textContent = 'Fair';
  } else if (strength < 4) {
    strengthBar.classList.add('good');
    strengthText.textContent = 'Good';
  } else {
    strengthBar.classList.add('strong');
    strengthText.textContent = 'Strong';
  }
}

/**
 * Show forgot password modal
 */
function showForgotPassword() {
  document.getElementById('forgotPasswordModal').style.display = 'block';
}

/**
 * Close forgot password modal
 */
function closeForgotPassword() {
  document.getElementById('forgotPasswordModal').style.display = 'none';
}

/**
 * Send reset email
 */
async function sendResetEmail() {
  const email = document.getElementById('resetEmail').value;
  if (!email) {
    showAlert('Please enter your email address', { type: 'warning' });
    return;
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/forgot-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    const data = await response.json();

    if (response.ok) {
      showAlert('Password reset link sent to ' + email, { type: 'success' });
      closeForgotPassword();
    } else {
      showAlert(data.error || 'Failed to send reset email', { type: 'error' });
    }
  } catch (error) {
    console.error('Reset email error:', error);
    showAlert('An error occurred. Please try again.', { type: 'error' });
  }
}

// Initialize tab functionality
tabButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    const tabName = btn.getAttribute('data-tab');
    switchTab(tabName);
  });
});

// Password strength checker
const signupPassword = document.getElementById('signupPassword');
if (signupPassword) {
  signupPassword.addEventListener('input', (e) => {
    checkPasswordStrength(e.target.value);
  });
}

// Close modal when clicking outside
window.addEventListener('click', (e) => {
  const modal = document.getElementById('forgotPasswordModal');
  if (e.target === modal) {
    closeForgotPassword();
  }
});

// Handle URL hash navigation
window.addEventListener('load', () => {
  const hash = window.location.hash.substring(1);
  if (hash === 'signup') {
    switchTab('signup');
  } else {
    switchTab('login');
  }
});

// --- SIGNUP LOGIC ---
if (signupForm) {
  signupForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // Stop the form from submitting normally
    
    // Clear previous errors
    displayError('');

    const name = document.getElementById('signupName').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const agreeTerms = document.getElementById('agreeTerms').checked;

    // Validation
    if (!name || !email || !password) {
      displayError('Please fill in all required fields.');
      return;
    }

    if (!agreeTerms) {
      displayError('Please agree to the Terms and Conditions to continue.');
      return;
    }

    if (password !== confirmPassword) {
      displayError('Passwords do not match. Please try again.');
      return;
    }

    if (password.length < 8) {
      displayError('Password must be at least 8 characters long.');
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      displayError('Please enter a valid email address.');
      return;
    }

    // Name validation (at least 2 characters)
    if (name.length < 2) {
      displayError('Name must be at least 2 characters long.');
      return;
    }

    // Password strength validation
    const passwordStrength = checkPasswordStrengthValue(password);
    if (passwordStrength < 2) {
      displayError('Password is too weak. Please use a stronger password.');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        // Success! Switch to login tab
        displayError('');
        showAlert('Signup successful! Please log in with your credentials.', { type: 'success' });
        switchTab('login');
        // Clear the signup form
        signupForm.reset();
        document.querySelector('.strength-fill').className = 'strength-fill';
        document.querySelector('.strength-text').textContent = 'Password strength';
      } else {
        // Show error message from server (e.g., "Email already exists")
        displayError(data.error || 'Signup failed');
      }
    } catch (error) {
      console.error('Signup error:', error);
      displayError('An error occurred. Please try again.');
    }
  });
}

// --- LOGIN LOGIC ---
if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    displayError('');

    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;

    // Basic validation
    if (!email || !password) {
      displayError('Please fill in all fields.');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        // !! SUCCESS: Save the token and user data !!
        localStorage.setItem('token', data.token);
        localStorage.setItem('userName', data.name);
        localStorage.setItem('userEmail', data.email);
        localStorage.setItem('userRole', data.role || 'user');
        
        // Redirect to the main app (archive). Also set server-side session for SSR pages
        try {
          const form = new FormData();
          form.append('token', data.token);
          // Ensure cookie-based session set, then redirect
          await fetch(`${API_BASE_URL}/auth`, { method: 'POST', body: form, credentials: 'include' });
        } catch (e) { /* ignore session sync errors; JWT is enough for API */ }
        window.location.href = '/archive';
      } else {
        displayError(data.error || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      displayError('An error occurred. Please try again.');
    }
  });
}

// --- LOGOUT LOGIC ---
// We can call this from any page
function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('userName');
  localStorage.removeItem('userEmail');
  localStorage.removeItem('userRole');
  window.location.href = '/auth';
}

// Add logout to a logout button if it exists
const logoutButton = document.getElementById('logoutButton');
if (logoutButton) {
  logoutButton.addEventListener('click', logout);
}

// --- SOCIAL LOGIN PLACEHOLDERS ---
// Google login
const googleBtn = document.querySelector('.google-btn');
if (googleBtn) {
  googleBtn.addEventListener('click', () => {
    showAlert('Google login integration coming soon!', { type: 'info' });
  });
}

// GitHub login
const githubBtn = document.querySelector('.github-btn');
if (githubBtn) {
  githubBtn.addEventListener('click', () => {
    showAlert('GitHub login integration coming soon!', { type: 'info' });
  });
}