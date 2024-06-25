function navigateTo(page) {
    window.location.href = page;
}

document.addEventListener('DOMContentLoaded', () => {
    // user information
    document.getElementById('user-location').textContent = 'Los Angeles, USA';
    document.getElementById('user-weather').textContent = 'Cloudy, 20°C';
    document.getElementById('user-gear').textContent = 'Advanced Rod, Reel, Bait, Tackle Box';
    document.getElementById('user-skill').textContent = 'Expert Fisherman';

    // saved search function if needed
    const savedSearches = document.getElementById('saved-searches');
    const newSearch = document.createElement('li');
    newSearch.textContent = 'Fishing techniques for experts';
    savedSearches.appendChild(newSearch);

    // handle search functionality
    const searchButton = document.querySelector('.search-bar button');
    const searchInput = document.querySelector('.search-bar input');
    const resultsContainer = document.querySelector('.content');

    searchButton.addEventListener('click', function() {
        const query = searchInput.value.trim();
        const userId = 1; // replace with dynamic user ID if available

        if (query) {
            fetch(`/api/search?q=${encodeURIComponent(query)}&user_id=${userId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        resultsContainer.innerHTML = `<p>${data.error}</p>`;
                    } else {
                        displayResults(data);
                    }
                })
                .catch(error => {
                    console.error('Error fetching search results:', error);
                    resultsContainer.innerHTML = `<p>There was an error fetching the search results.</p>`;
                });
        } else {
            resultsContainer.innerHTML = `<p>Please enter a search query.</p>`;
        }
    });

    function displayResults(results) {
        resultsContainer.innerHTML = '';
        if (results.items && results.items.length > 0) {
            results.items.forEach(result => {
                const resultElement = document.createElement('div');
                resultElement.classList.add('search-result');
                resultElement.innerHTML = `
                    <h3>${result.title}</h3>
                    <p>${result.snippet}</p>
                    <a href="${result.link}" target="_blank">Read more</a>
                `;
                resultsContainer.appendChild(resultElement);
            });
        } else {
            resultsContainer.innerHTML = `<p>No results found.</p>`;
        }
    }
});
