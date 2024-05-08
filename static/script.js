/**
 * Initiates a search for Venture Capitals based on the user's query.
 */
function searchVCs() {
    const searchText = document.getElementById('searchQuery').value;
    const payload = { text: searchText };

    fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        console.log("Server response:", data); // log the full response from the server
        if (data.error) {
            throw new Error(data.error);
        }
        displayResults(data);
    })
    .catch(error => {
        console.error('Fetch error:', error.message);
        displayError(error.message);
    });
}

/**
 * Displays search results or errors on the webpage.
 * @param {Object} data - The data object containing the search results.
 */
function displayResults(data) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = '';  // clear previous results

    if (!data || !data.similar_vcs || !Array.isArray(data.similar_vcs)) {
        const errorElement = document.createElement('div');
        errorElement.textContent = 'Error: No results found or data format incorrect.';
        resultsContainer.appendChild(errorElement);
        console.error('Error or incorrect data format:', data);
        return;
    }

    const list = document.createElement('ol');  // create an ordered list
    resultsContainer.appendChild(list);  // append the list to the results container

    data.similar_vcs.forEach(result => {
        console.log("URL:", result.url);
        const listItem = document.createElement('li');  // create a list item for each result
        const linkElement = document.createElement('a');
        linkElement.href = result.url;
        linkElement.textContent = result.url;
        linkElement.target = "_blank";
        listItem.appendChild(linkElement);
        list.appendChild(listItem);  // append the list item to the list
    });
}

/**
 * Displays error messages on the webpage.
 * @param {string} message - The error message to display.
 */
function displayError(message) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = ''; // clear previous results
    const errorElement = document.createElement('div');
    errorElement.textContent = 'Error: ' + message;
    resultsContainer.appendChild(errorElement);
    console.error('Displayed Error:', message); // log displayed error message
}
