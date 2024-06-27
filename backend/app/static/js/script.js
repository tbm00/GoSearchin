// app.static.js.script.js

function navigateTo(page) {
    window.location.href = page;
}

document.addEventListener('DOMContentLoaded', () => {
    // User information
    document.getElementById('user-location').textContent = 'Los Angeles, USA';
    document.getElementById('user-weather').textContent = 'Cloudy, 20°C';
    document.getElementById('user-gear').textContent = 'Advanced Rod, Reel, Bait, Tackle Box';
    document.getElementById('user-skill').textContent = 'Expert Fisherman';

    // Saved search function if needed
    const savedSearches = document.getElementById('saved-searches');
    if (savedSearches) {
        const newSearch = document.createElement('li');
        newSearch.textContent = 'Fishing techniques for experts';
        savedSearches.appendChild(newSearch);
    }

    // Handle search functionality
    const searchButton = document.querySelector('.search-bar button');
    const searchInput = document.querySelector('.search-bar input');
    const resultsContainer = document.querySelector('.content');

    searchButton.addEventListener('click', performSearch);

    function performSearch() {
        const query = searchInput.value.trim();
        if (query) {
            searchGoogle(query);
        } else {
            resultsContainer.innerHTML = `<p>Please enter a search query.</p>`;
        }
    }

    function searchGoogle(query) {
        fetch(`/api/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => displayResults(data))
            .catch(error => {
                console.error('Error fetching search results:', error);
                resultsContainer.innerHTML = `<p>There was an error fetching the search results.</p>`;
            });
    }

    function toggleOption(button) {
        button.classList.toggle('selected');
        
        let selectedCategories = [];
        document.querySelectorAll('.sidebar-option.selected').forEach(option => {
            selectedCategories.push(option.dataset.category);
        });
    
        // Here you can update your search parameters based on selectedCategories
        // For example, you can update a hidden input field that gets submitted with the search
        // Or you can use these categories to refine the search query in some other way
        console.log('Selected Categories:', selectedCategories);
    }
    

    function displayResults(data) {
        resultsContainer.innerHTML = '';
        if (data.error) {
            resultsContainer.innerHTML = `<p>${data.error}</p>`;
        } else if (data.items && data.items.length > 0) {
            data.items.forEach(result => {
                const resultElement = document.createElement('div');
                resultElement.classList.add('search-result');
                resultElement.innerHTML = `
                    <h3><a href="${result.link}" target="_blank">${result.title}</a></h3>
                    <p>${result.snippet}</p>
                `;
                resultsContainer.appendChild(resultElement);
            });
        } else {
            resultsContainer.innerHTML = `<p>No results found.</p>`;
        }
    }
});
