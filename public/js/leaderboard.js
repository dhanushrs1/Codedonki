class AdvancedLeaderboard {
  constructor() {
    this.leaderboardData = [];
    this.updateInterval = null;
    this.isLive = true;
    this.lastUpdateTime = null;
    
    this.elements = {
      podiumSection: document.getElementById('podium-section'),
      leaderboardList: document.getElementById('leaderboard-list'),
      emptyState: document.getElementById('empty-state'),
      liveBadge: document.getElementById('live-badge'),
      totalPlayers: document.getElementById('total-players'),
      totalXp: document.getElementById('total-xp'),
      firstPlace: document.getElementById('first-place'),
      secondPlace: document.getElementById('second-place'),
      thirdPlace: document.getElementById('third-place')
    };
    
    this.init();
  }

  async init() {
    await this.loadLeaderboard();
    this.startLiveUpdates();
    this.setupEventListeners();
  }

  async loadLeaderboard() {
      try {
        const response = await apiFetch('/api/leaderboard');
        if (!response.ok) {
          throw new Error('Failed to fetch leaderboard data.');
        }
        
      const data = await response.json();
      this.leaderboardData = data;
      this.renderLeaderboard();
      this.updateStats();
      
    } catch (error) {
      console.error('Leaderboard error:', error);
      this.showError(error.message);
    }
  }

  renderLeaderboard() {
    if (this.leaderboardData.length === 0) {
      this.showEmptyState();
          return;
        }

    this.hideEmptyState();
    this.renderPodium();
    this.renderLeaderboardList();
  }

  renderPodium() {
    const topThree = this.leaderboardData.slice(0, 3);
    
    // Update podium positions
    this.updatePodiumPlace(this.elements.firstPlace, topThree[0], 1);
    this.updatePodiumPlace(this.elements.secondPlace, topThree[1], 2);
    this.updatePodiumPlace(this.elements.thirdPlace, topThree[2], 3);
  }

  updatePodiumPlace(element, user, rank) {
    if (!user) {
      element.style.display = 'none';
      return;
    }
    
    element.style.display = 'flex';
    
    const avatar = element.querySelector('.avatar-placeholder');
    const playerName = element.querySelector('.player-name');
    const xpValue = element.querySelector('.xp-value');
    
    // Update avatar
    if (user.avatar_url) {
      avatar.innerHTML = `<img src="${API_BASE_URL}${user.avatar_url}" alt="${user.name}">`;
    } else {
      avatar.innerHTML = `<i class="fas fa-user"></i>`;
    }
    
    // Update player info
    playerName.textContent = user.name;
    xpValue.textContent = this.formatNumber(user.xp);
    
    // Add animation for updates
    element.classList.add('updated');
    setTimeout(() => element.classList.remove('updated'), 1000);
  }

  renderLeaderboardList() {
    const listElement = this.elements.leaderboardList;
    listElement.innerHTML = '';
    
    // Show only players ranked 4-50
    const regularPlayers = this.leaderboardData.slice(3, 50);
    
    if (regularPlayers.length === 0) {
      listElement.innerHTML = `
        <div class="no-more-players">
          <p>More players will appear here as they join!</p>
        </div>
      `;
      return;
    }
    
    regularPlayers.forEach((user, index) => {
      const rank = index + 4;
      const item = this.createLeaderboardItem(user, rank);
      listElement.appendChild(item);
    });
  }

  createLeaderboardItem(user, rank) {
    const item = document.createElement('div');
    item.className = 'leaderboard-item';
    
    // Calculate XP progress (assuming max XP for current level)
    const xpProgress = this.calculateXpProgress(user.xp);
    
    item.innerHTML = `
      <div class="rank ${rank <= 10 ? 'top-rank' : ''}">${rank}</div>
      <div class="avatar">
        ${user.avatar_url ? 
          `<img src="${API_BASE_URL}${user.avatar_url}" alt="${user.name}">` : 
          `<i class="fas fa-user"></i>`
        }
      </div>
      <div class="player-info">
        <div class="player-name">${user.name}</div>
        <div class="player-level">Level ${this.calculateLevel(user.xp)}</div>
      </div>
      <div class="xp-info">
        <div class="xp-amount">${this.formatNumber(user.xp)}</div>
        <div class="xp-progress">
          <div class="xp-progress-bar" style="width: ${xpProgress}%"></div>
        </div>
      </div>
    `;
    
    // Add entrance animation
    item.style.opacity = '0';
    item.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
      item.style.transition = 'all 0.5s ease';
      item.style.opacity = '1';
      item.style.transform = 'translateY(0)';
    }, Math.random() * 500);
    
    return item;
  }

  calculateLevel(xp) {
    // Simple level calculation (can be made more complex)
    return Math.floor(xp / 100) + 1;
  }

  calculateXpProgress(xp) {
    const currentLevel = this.calculateLevel(xp);
    const currentLevelXp = (currentLevel - 1) * 100;
    const nextLevelXp = currentLevel * 100;
    const progressXp = xp - currentLevelXp;
    const levelXpRange = nextLevelXp - currentLevelXp;
    
    return Math.min((progressXp / levelXpRange) * 100, 100);
  }

  formatNumber(num) {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  }

  updateStats() {
    const totalPlayers = this.leaderboardData.length;
    const totalXp = this.leaderboardData.reduce((sum, user) => sum + user.xp, 0);
    
    this.elements.totalPlayers.textContent = totalPlayers;
    this.elements.totalXp.textContent = this.formatNumber(totalXp);
  }

  showEmptyState() {
    this.elements.podiumSection.style.display = 'none';
    this.elements.emptyState.style.display = 'block';
  }

  hideEmptyState() {
    this.elements.podiumSection.style.display = 'block';
    this.elements.emptyState.style.display = 'none';
  }

  showError(message) {
    this.elements.leaderboardList.innerHTML = `
      <div class="error-state">
        <i class="fas fa-exclamation-triangle"></i>
        <h3>Error Loading Leaderboard</h3>
        <p>${message}</p>
        <button class="btn btn-primary" onclick="location.reload()">
          <i class="fas fa-refresh"></i>
          Retry
        </button>
      </div>
    `;
  }

  startLiveUpdates() {
    // Update every 30 seconds
    this.updateInterval = setInterval(() => {
      this.loadLeaderboard();
      this.updateLiveBadge();
    }, 30000);
    
    // Initial live badge update
    this.updateLiveBadge();
  }

  updateLiveBadge() {
    const now = new Date();
    this.lastUpdateTime = now;
    
    // Add pulse effect
    this.elements.liveBadge.classList.add('pulse');
    setTimeout(() => {
      this.elements.liveBadge.classList.remove('pulse');
    }, 1000);
  }

  setupEventListeners() {
    // Add click effects to leaderboard items
    this.elements.leaderboardList.addEventListener('click', (e) => {
      const item = e.target.closest('.leaderboard-item');
      if (item) {
        item.classList.add('clicked');
        setTimeout(() => item.classList.remove('clicked'), 200);
      }
    });

    // Add hover effects to podium
    const podiumPlaces = [this.elements.firstPlace, this.elements.secondPlace, this.elements.thirdPlace];
    podiumPlaces.forEach(place => {
      place.addEventListener('mouseenter', () => {
        place.classList.add('hovered');
      });
      
      place.addEventListener('mouseleave', () => {
        place.classList.remove('hovered');
      });
    });
  }


  destroy() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
    }
  }
}

// Initialize the advanced leaderboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.leaderboard = new AdvancedLeaderboard();
});

// Clean up when page unloads
window.addEventListener('beforeunload', () => {
  if (window.leaderboard) {
    window.leaderboard.destroy();
  }
  });