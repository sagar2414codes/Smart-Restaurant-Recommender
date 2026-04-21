/* ============================================
   Smart Restaurant Recommender - JavaScript
   ============================================ */

let currentResults = [];
let allCuisines = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadCuisines();
    loadBudgetRange();
    loadStats();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    const budgetSlider = document.getElementById('budgetSlider');
    const maxResultsSlider = document.getElementById('maxResults');
    const searchInput = document.getElementById('searchInput');

    budgetSlider.addEventListener('input', updateBudgetDisplay);
    maxResultsSlider.addEventListener('input', updateResultsDisplay);
    
    searchInput.addEventListener('input', function() {
        if (this.value.length > 1) {
            quickSearch(this.value);
        } else {
            document.getElementById('searchResults').classList.remove('active');
        }
    });
}

// Load cuisines
async function loadCuisines() {
    try {
        const response = await fetch('/api/cuisines');
        const data = await response.json();
        allCuisines = data.cuisines;
        
        const container = document.getElementById('cuisinesContainer');
        container.innerHTML = '';
        
        allCuisines.forEach(cuisine => {
            const btn = document.createElement('button');
            btn.className = 'cuisine-btn';
            btn.textContent = cuisine;
            btn.onclick = function() {
                this.classList.toggle('active');
            };
            container.appendChild(btn);
        });
    } catch (error) {
        console.error('Error loading cuisines:', error);
    }
}

// Load budget range
async function loadBudgetRange() {
    try {
        const response = await fetch('/api/budget-range');
        const data = await response.json();
        
        document.getElementById('minBudget').value = data.min;
        document.getElementById('maxBudget').value = data.max;
        document.getElementById('budgetSlider').max = data.max;
        document.getElementById('budgetSlider').value = data.max / 2;
        
        updateBudgetDisplay();
    } catch (error) {
        console.error('Error loading budget range:', error);
    }
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        document.getElementById('totalRestaurants').textContent = data.total_restaurants.toLocaleString();
        document.getElementById('totalCuisines').textContent = data.unique_cuisines;
        document.getElementById('avgRating').textContent = data.avg_rating.toFixed(1);
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// Update budget display
function updateBudgetDisplay() {
    const slider = document.getElementById('budgetSlider');
    const minInput = document.getElementById('minBudget');
    const maxInput = document.getElementById('maxBudget');
    
    const min = parseFloat(minInput.value) || 0;
    const max = parseFloat(maxInput.value) || slider.max;
    
    document.getElementById('budgetDisplay').textContent = `₹${min.toLocaleString('en-IN')} - ₹${max.toLocaleString('en-IN')}`;
}

// Update results display
function updateResultsDisplay() {
    const value = document.getElementById('maxResults').value;
    document.getElementById('resultsDisplay').textContent = value;
}

// Quick search
async function quickSearch(query) {
    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query, limit: 10 })
        });
        
        const data = await response.json();
        const searchResults = document.getElementById('searchResults');
        
        if (data.restaurants && data.restaurants.length > 0) {
            searchResults.innerHTML = data.restaurants.map(r => `
                <div class="search-result-item" onclick="selectSearchResult('${r.name}')">
                    <strong>${r.name}</strong> <br>
                    <small>${r.city} • ${r.cuisines.join(', ')}</small>
                </div>
            `).join('');
            searchResults.classList.add('active');
        } else {
            searchResults.innerHTML = '<div class="search-result-item">No results found</div>';
            searchResults.classList.add('active');
        }
    } catch (error) {
        console.error('Search error:', error);
    }
}

// Select from search results
function selectSearchResult(name) {
    document.getElementById('searchInput').value = name;
    document.getElementById('searchResults').classList.remove('active');
}

// Search restaurants
async function searchRestaurants() {
    const selectedCuisines = Array.from(document.querySelectorAll('.cuisine-btn.active'))
        .map(btn => btn.textContent);
    
    if (selectedCuisines.length === 0) {
        alert('Please select at least one cuisine!');
        return;
    }
    
    const minBudget = parseFloat(document.getElementById('minBudget').value) || 0;
    const maxBudget = parseFloat(document.getElementById('maxBudget').value) || 10000;
    const minRating = parseFloat(document.getElementById('minRating').value) || 0;
    const maxResults = parseInt(document.getElementById('maxResults').value) || 20;
    
    // Show loading state
    document.getElementById('loadingState').style.display = 'flex';
    document.getElementById('noResultsState').style.display = 'none';
    document.getElementById('resultsContainer').style.display = 'none';
    
    try {
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                cuisines: selectedCuisines,
                minBudget: minBudget,
                maxBudget: maxBudget,
                minRating: minRating,
                maxResults: maxResults
            })
        });
        
        const data = await response.json();
        
        if (data.restaurants && data.restaurants.length > 0) {
            currentResults = data.restaurants;
            displayResults(data.restaurants);
            document.getElementById('exportBtn').style.display = 'block';
        } else {
            showNoResults();
        }
    } catch (error) {
        console.error('Search error:', error);
        alert('Error fetching recommendations. Please try again.');
    } finally {
        document.getElementById('loadingState').style.display = 'none';
    }
}

// Display results
function displayResults(restaurants) {
    const resultsTitle = document.getElementById('resultsTitle');
    const resultsCount = document.getElementById('resultsCount');
    const restaurantsList = document.getElementById('restaurantsList');
    
    resultsTitle.textContent = `🎯 Top Recommendations`;
    resultsCount.textContent = `${restaurants.length} restaurant${restaurants.length !== 1 ? 's' : ''} found`;
    
    restaurantsList.innerHTML = restaurants.map((restaurant, index) => `
        <div class="restaurant-card" onclick="showDetails(${index})">
            <div class="card-header">
                <div class="card-name">${index + 1}. ${restaurant.name}</div>
                <div class="card-rating ${restaurant.rating === 0 ? 'no-rating' : ''}">
                    ${restaurant.rating > 0 ? `${restaurant.rating.toFixed(1)}/5` : 'N/A'}
                </div>
            </div>
            
            <div class="card-location">📍 ${restaurant.city}</div>
            
            <div class="card-address">${restaurant.address}</div>
            
            <div class="card-cuisines">
                ${restaurant.cuisines.map(c => `<span class="cuisine-tag">${c}</span>`).join('')}
            </div>
            
            <div class="card-footer">
                <div class="card-cost">₹${restaurant.cost.toLocaleString('en-IN')}</div>
                <div class="card-features">
                    ${restaurant.tableBooking ? '<span class="feature-badge">📕 Booking</span>' : ''}
                    ${restaurant.onlineDelivery ? '<span class="feature-badge">🛵 Delivery</span>' : ''}
                </div>
            </div>
        </div>
    `).join('');
    
    document.getElementById('noResultsState').style.display = 'none';
    document.getElementById('resultsContainer').style.display = 'block';
}

// Show no results
function showNoResults() {
    document.getElementById('noResultsState').innerHTML = `
        <div class="empty-state">
            <span class="empty-icon">😅</span>
            <h3>No restaurants found</h3>
            <p>Try adjusting your filters or budget range</p>
        </div>
    `;
    document.getElementById('noResultsState').style.display = 'flex';
    document.getElementById('resultsContainer').style.display = 'none';
}

// Show restaurant details in modal
function showDetails(index) {
    const restaurant = currentResults[index];
    const modalBody = document.getElementById('modalBody');
    
    modalBody.innerHTML = `
        <div style="text-align: center;">
            <h2>${restaurant.name}</h2>
            <p style="color: #999; margin-bottom: 20px;">${restaurant.city}</p>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                <div>
                    <div style="font-size: 2em; color: #FFD93D;">${restaurant.rating > 0 ? '⭐'.repeat(Math.round(restaurant.rating)) : 'Not rated'}</div>
                    <div style="color: #999;">Rating: ${restaurant.rating > 0 ? restaurant.rating.toFixed(1) + '/5' : 'N/A'}</div>
                </div>
                <div>
                    <div style="font-size: 1.5em; color: #4D96FF; font-weight: bold;">₹${restaurant.cost.toLocaleString('en-IN')}</div>
                    <div style="color: #999;">Cost for two</div>
                </div>
            </div>
            
            <div style="background: #f5f7fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <p><strong>Address:</strong><br> ${restaurant.address}</p>
                <p style="margin-top: 10px;"><strong>Cuisines:</strong></p>
                <div style="margin-top: 8px;">
                    ${restaurant.cuisines.map(c => `<span style="background: #FF6B6B; color: white; padding: 4px 10px; border-radius: 12px; margin-right: 8px; font-size: 0.9em;">${c}</span>`).join('')}
                </div>
            </div>
            
            <div style="display: flex; gap: 10px; margin-top: 20px;">
                ${restaurant.tableBooking ? '<div style="background: #6BCB77; color: white; padding: 10px 15px; border-radius: 8px; flex: 1;">📕 Table Booking Available</div>' : ''}
                ${restaurant.onlineDelivery ? '<div style="background: #6BCB77; color: white; padding: 10px 15px; border-radius: 8px; flex: 1;">🛵 Online Delivery Available</div>' : ''}
            </div>
            
            <p style="margin-top: 20px; color: #999; font-size: 0.9em;">👥 ${restaurant.votes} people reviewed this restaurant</p>
        </div>
    `;
    
    document.getElementById('restaurantModal').style.display = 'flex';
}

// Close modal
function closeModal() {
    document.getElementById('restaurantModal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('restaurantModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
};

// Export results
async function exportResults() {
    try {
        const response = await fetch('/api/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ restaurants: currentResults })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const blob = new Blob([data.csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'restaurant_recommendations.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        }
    } catch (error) {
        console.error('Export error:', error);
        alert('Error exporting results');
    }
}
