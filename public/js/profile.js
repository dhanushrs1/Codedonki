document.addEventListener('DOMContentLoaded', () => {
  // Get all form elements
  const profileForm = document.getElementById('profileForm');
  const avatarForm = document.getElementById('avatarForm');
  
  const nameInput = document.getElementById('name');
  const emailInput = document.getElementById('email');
  const xpInput = document.getElementById('xp');
  const avatarPreview = document.getElementById('avatar-preview');
  const avatarFile = document.getElementById('avatar-file');
  
  const alertContainer = document.getElementById('popup-alert');

  /**
   * Helper function to display alert messages (uses global showAlert)
   */
  function showMessage(message, type = 'info') {
    showAlert(message, { type: type });
  }

  /**
   * Load the user's current profile data
   */
  async function loadProfile() {
    try {
      const response = await apiFetch('/api/profile');
      if (!response.ok) {
        throw new Error('Failed to load profile. Please log in again.');
      }
      
      const profile = await response.json();
      
      // Populate the form fields
      nameInput.value = profile.name || '';
      emailInput.value = profile.email || '';
      xpInput.value = profile.xp || 0;
      
      // Profile data loaded successfully
      
      // Set avatar image
      if (profile.avatar_url) {
        avatarPreview.src = `${API_BASE_URL}${profile.avatar_url}`;
      } else {
        avatarPreview.src = `${API_BASE_URL}/uploads/profile.png`;
      }
      
    } catch (error) {
      console.error('Profile load error:', error);
      showMessage(error.message, 'error');
    }
  }

  /**
   * Handle profile update (name change)
   */
  profileForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const newName = nameInput.value.trim();

    if (!newName) {
      showMessage('Please enter a valid name', 'error');
      return;
    }

    // Disable button during submission
    const submitBtn = profileForm.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Saving...';

    try {
      const response = await apiFetch('/api/profile', {
        method: 'PUT',
        body: JSON.stringify({ name: newName })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        showMessage('Profile updated successfully!', 'success');
        // Update the name in localStorage for dashboard
        localStorage.setItem('userName', data.name);
      } else {
        throw new Error(data.error || 'Failed to update profile');
      }
    } catch (error) {
      showMessage(error.message, 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
    }
  });

  /**
   * Handle avatar upload
   */
  avatarForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!avatarFile.files[0]) {
      showMessage('Please select an image file to upload', 'error');
      return;
    }

    // Validate file type
    const file = avatarFile.files[0];
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif'];
    if (!validTypes.includes(file.type)) {
      showMessage('Please select a valid image file (PNG, JPG, or GIF)', 'error');
      return;
    }

    // Validate file size (max 5MB)
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) {
      showMessage('Image size must be less than 5MB', 'error');
      return;
    }
    
    const formData = new FormData();
    formData.append('avatar', file);

    // Disable button during upload
    const submitBtn = avatarForm.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Uploading...';

    try {
      const response = await apiFetch('/api/profile/avatar', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (response.ok) {
        showMessage('Avatar updated successfully!', 'success');
        // Update the preview with a cache-busting timestamp
        avatarPreview.src = `${API_BASE_URL}${data.avatar_url}?t=${Date.now()}`;
        // Clear file input
        avatarFile.value = '';
        document.getElementById('selected-file').classList.remove('show');
      } else {
        throw new Error(data.error || 'Failed to upload avatar');
      }
    } catch (error) {
      showMessage(error.message, 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
    }
  });

  /**
   * Handle password change form
   */
  const passwordForm = document.getElementById('passwordForm');
  passwordForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const currentPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    // Validation
    if (!currentPassword || !newPassword || !confirmPassword) {
      showMessage('Please fill in all password fields', 'error');
      return;
    }

    if (newPassword !== confirmPassword) {
      showMessage('New passwords do not match', 'error');
      return;
    }

    if (newPassword.length < 6) {
      showMessage('New password must be at least 6 characters long', 'error');
      return;
    }

    // Disable button during submission
    const submitBtn = passwordForm.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Changing...';

    try {
      const response = await apiFetch('/api/profile/password', {
        method: 'PUT',
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        showMessage('Password changed successfully!', 'success');
        // Clear form
        passwordForm.reset();
      } else {
        throw new Error(data.error || 'Failed to change password');
      }
    } catch (error) {
      showMessage(error.message, 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
    }
  });

  // Preview avatar on file selection
  avatarFile.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      const reader = new FileReader();
      reader.onload = (event) => {
        // Show preview immediately
        avatarPreview.src = event.target.result;
      };
      reader.readAsDataURL(e.target.files[0]);
    }
  });

  // Initialize profile
  loadProfile();
});
