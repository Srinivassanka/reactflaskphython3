document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const textInput = document.getElementById('textInput');
    const operationSelect = document.getElementById('operationSelect');
    const processBtn = document.getElementById('processBtn');
    const resultCard = document.getElementById('resultCard');
    const errorCard = document.getElementById('errorCard');
    const operationName = document.getElementById('operationName');
    const originalText = document.getElementById('originalText');
    const resultText = document.getElementById('resultText');
    const errorText = document.getElementById('errorText');

    // Check if API is available
    fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            console.log('API Health Check:', data);
        })
        .catch(error => {
            console.error('API Health Check Failed:', error);
            showError('API is not available. Please try again later.');
        });

    // Add event listener to the process button
    processBtn.addEventListener('click', processText);

    // Process text function
    function processText() {
        // Hide any previous results or errors
        resultCard.classList.add('d-none');
        errorCard.classList.add('d-none');

        // Get the text and operation
        const text = textInput.value.trim();
        const operation = operationSelect.value;

        // Validate input
        if (!text) {
            showError('Please enter some text to process.');
            return;
        }

        // Show loading state
        processBtn.disabled = true;
        processBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';

        // Send request to the backend
        fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                operation: operation
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server returned ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            // Display the result
            displayResult(data);
        })
        .catch(error => {
            console.error('Error:', error);
            showError(error.message || 'An error occurred while processing your request.');
        })
        .finally(() => {
            // Reset button state
            processBtn.disabled = false;
            processBtn.innerHTML = '<i class="fas fa-cogs"></i> Process Text';
        });
    }

    // Display the result
    function displayResult(data) {
        // Set the operation name based on the operation
        let operationDisplayName = '';
        switch(data.operation) {
            case 'uppercase':
                operationDisplayName = 'Convert to UPPERCASE';
                break;
            case 'lowercase':
                operationDisplayName = 'Convert to lowercase';
                break;
            case 'reverse':
                operationDisplayName = 'Reverse text';
                break;
            case 'wordcount':
                operationDisplayName = 'Count words';
                break;
            default:
                operationDisplayName = data.operation;
        }

        operationName.textContent = operationDisplayName;
        originalText.textContent = data.original;
        
        // Handle different result types
        if (typeof data.result === 'number') {
            resultText.textContent = `${data.result} words`;
        } else {
            resultText.textContent = data.result;
        }

        // Show the result card
        resultCard.classList.remove('d-none');

        // Scroll to the result
        resultCard.scrollIntoView({ behavior: 'smooth' });
    }

    // Show error message
    function showError(message) {
        errorText.textContent = message;
        errorCard.classList.remove('d-none');
        errorCard.scrollIntoView({ behavior: 'smooth' });
    }
});
