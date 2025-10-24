// Wait for the DOM to be fully loaded before running scripts
document.addEventListener('DOMContentLoaded', () => {
    const lessonForm = document.getElementById('lessonForm');
    const categorySelect = document.getElementById('category');
    const statusMessage = document.getElementById('status-message');
  
    // --- 1. Check Admin Status and Load Categories ---
    (async function initAdminPage() {
      try {
        // Check if user is an admin
        const profileResponse = await apiFetch('/api/profile');
        if (!profileResponse.ok) throw new Error('Could not fetch profile.');
        
        const profile = await profileResponse.json();
        if (profile.role !== 'admin') {
          // If not admin, redirect to the main archive
          showAlert('You do not have permission to access this page.', { type: 'error' });
          setTimeout(() => { window.location.href = '../archive.html'; }, 1500);
          return;
        }
        
        // If admin, load the categories
        await loadCategories();
  
      } catch (error) {
        console.error('Admin init error:', error);
        window.location.href = '../auth.html'; // Redirect to auth on any auth error
      }
    })();
  
    // --- 2. Function to Load Categories ---
    async function loadCategories() {
      try {
        const response = await apiFetch('/api/categories');
        if (!response.ok) throw new Error('Failed to load categories');
        
        const categories = await response.json();
        
        categorySelect.innerHTML = '<option value="">Select a category</option>'; // Clear loading text
        
        if (categories.length === 0) {
          categorySelect.innerHTML = '<option value="">No categories found</option>';
          return;
        }
  
        categories.forEach(category => {
          const option = document.createElement('option');
          option.value = category.id;
          option.textContent = category.name;
          categorySelect.appendChild(option);
        });
  
      } catch (error) {
        console.error('Error loading categories:', error);
        categorySelect.innerHTML = '<option value="">Error loading categories</option>';
      }
    }
  
    // --- 3. Function to Handle Form Submission ---
    if (lessonForm) {
      lessonForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Stop default form submission
        
        // We use FormData because we are sending a file
        const formData = new FormData(lessonForm);
  
        // Clear previous status
        statusMessage.textContent = 'Uploading...';
        statusMessage.className = '';
        statusMessage.style.display = 'block';
  
        try {
          const response = await apiFetch('/api/admin/lessons', {
            method: 'POST',
            body: formData, // No 'Content-Type' header, browser sets it for FormData
          });
  
          const data = await response.json();
  
          if (response.ok) {
            statusMessage.textContent = 'Lesson created successfully!';
            statusMessage.className = 'success';
            lessonForm.reset(); // Clear the form
          } else {
            throw new Error(data.error || 'Failed to create lesson');
          }
        } catch (error) {
          console.error('Lesson creation error:', error);
          statusMessage.textContent = error.message;
          statusMessage.className = 'error';
        }
      });
    }
  });