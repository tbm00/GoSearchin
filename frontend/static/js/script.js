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

    const page = window.location.pathname.split("/").pop();

    if (page === 'weather.html') {
        fetchWeather();
    } else if (page === 'location.html') {
        fetchLocation();
    } else if (page === 'fish.html') {
        fetchFish();
    }

    function fetchWeather() {
        // Fetch weather data from your API
        fetch('/api/weather')
            .then(response => response.json())
            .then(data => {
                const weatherInfo = document.getElementById('weather-info');
                weatherInfo.innerHTML = `
                    <h3>${data.location}</h3>
                    <p>${data.condition}</p>
                    <p>${data.temperature}°C</p>
                `;
            })
            .catch(error => console.error('Error fetching weather data:', error));
    }

    function fetchLocation() {
        // Fetch location data from your API
        fetch('/api/location')
            .then(response => response.json())
            .then(data => {
                const locationInfo = document.getElementById('location-info');
                locationInfo.innerHTML = `
                    <h3>${data.city}, ${data.country}</h3>
                    <div id="map" style="height: 400px; width: 100%;"></div>
                `;
                // Initialize map here using the coordinates from data
                const map = new google.maps.Map(document.getElementById('map'), {
                    center: { lat: data.latitude, lng: data.longitude },
                    zoom: 8
                });
            })
            .catch(error => console.error('Error fetching location data:', error));
    }

    function fetchFish() {
        // Fetch fish data from your API
        fetch('/api/fish')
            .then(response => response.json())
            .then(data => {
                const fishList = document.getElementById('fish-list');
                data.fish.forEach(fish => {
                    const fishItem = document.createElement('div');
                    fishItem.classList.add('fish-item');
                    fishItem.innerHTML = `
                        <h3>${fish.name}</h3>
                        <p>${fish.description}</p>
                    `;
                    fishList.appendChild(fishItem);
                });
            })
            .catch(error => console.error('Error fetching fish data:', error));
    }
});
