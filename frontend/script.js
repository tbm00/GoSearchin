function navigateTo(page) {
    window.location.href = page;
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('user-location').textContent = 'Los Angeles, USA';
    document.getElementById('user-weather').textContent = 'Cloudy, 20°C';
    document.getElementById('user-gear').textContent = 'Advanced Rod, Reel, Bait, Tackle Box';
    document.getElementById('user-skill').textContent = 'Expert Fisherman';

    const savedSearches = document.getElementById('saved-searches');
    const newSearch = document.createElement('li');
    newSearch.textContent = 'Fishing techniques for experts';
    savedSearches.appendChild(newSearch);
});
