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

    if (Array.isArray(results)) { // Check if results is an array
        results.forEach(result => {
            const resultElement = document.createElement('div');
            resultElement.textContent = `URL: ${result.url}, Distance: ${result.distance}`;
            resultsContainer.appendChild(resultElement);
        });
    } else {
        // If results is not an array, display an error message
        const errorElement = document.createElement('div');
        errorElement.textContent = 'No results found.';
        resultsContainer.appendChild(errorElement);
    }
}
