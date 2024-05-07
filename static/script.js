function searchVCs() {
    const searchText = document.getElementById('searchQuery').value;
    const payload = { text: searchText };
    console.log("Request payload:", payload);  // Log the request payload

    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        console.log("Response:", data);  // Log the response data
        displayResults(data); // Pass the received data to the displayResults function
    })
    .catch(error => console.error('Error:', error));
}

// Define the displayResults function
function displayResults(results) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = ''; // Clear previous results

    // Only display the top three results
    results.slice(0, 3).forEach(result => {
        const resultElement = document.createElement('a'); // Create an anchor element for clickable links
        resultElement.href = result.url; // Set href to the result URL
        resultElement.textContent = `URL: ${result.url}`; // Set the display text
        resultElement.target = "_blank"; // Open in new tab
        resultsContainer.appendChild(resultElement);
        resultsContainer.appendChild(document.createElement('br')); // Add a line break for spacing
    });

    if (results.length === 0) {
        // If no results, display an error message
        const errorElement = document.createElement('div');
        errorElement.textContent = 'No results found.';
        resultsContainer.appendChild(errorElement);
    }
}
