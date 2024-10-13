//Initialize variables when loading the document
document.addEventListener('DOMContentLoaded', function() {

    const csvFileInput = document.getElementById('csv-file');
    const csvLabel = document.getElementById('csv-label');
    const excelFileInput = document.getElementById('excel-file');
    const excelLabel = document.getElementById('excel-label');
    const inputPrompt = document.getElementById('prompt');
    const submitButtonCSV = document.getElementById("csv-button");
    const submitButtonExcel =  document.getElementById("excel-button");
    const csvForm = this.getElementById('csvForm');
    const excelForm = this.getElementById('excelForm');
    const generatedContent = this.getElementById('generated-query');
    let csvContent;
    let excelContent;


    submitButtonCSV.textContent = 'Submit CSV'; // Change button text
    submitButtonCSV.disabled = false;
    submitButtonExcel.textContent = 'Submit Excel'; // Change button text
    submitButtonExcel.disabled = false;

    document.getElementById('success-message').textContent = '';
    document.getElementById('error-message').textContent = '';

    // Event listener for CSV file input
    csvFileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            const fileName = this.files[0].name;
            csvLabel.textContent = fileName;  // Update label with the file name
            excelFileInput.disabled = true;   // Disable the Excel input
            excelLabel.classList.add('disabled'); // Add disabled class to grey out label
        } else {
            submitButtonCSV.textContent = 'Submit'; // Change button text
            submitButtonCSV.disabled = false;
            csvLabel.textContent = "Upload CSV File"; // Reset label if no file is selected
            excelFileInput.disabled = false;  // Re-enable the Excel input
            excelLabel.classList.remove('disabled'); // Remove disabled class
        }
    });

    // Event listener for Excel file input
    excelFileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            const fileName = this.files[0].name;
            excelLabel.textContent = fileName;  // Update label with the file name
            csvFileInput.value = "";            // Unselect CSV file
            csvLabel.textContent = "Upload CSV File"; // Reset CSV label
            csvFileInput.disabled = true;   // Disable CSV input
            csvLabel.classList.add('disabled'); // Add disabled class to grey out label
        } else {
            excelLabel.textContent = "Upload Excel File"; // Reset label if no file is selected
        }

        // Disable CSV input if Excel file is selected
        csvFileInput.disabled = this.files.length > 0;   
        if (csvFileInput.disabled) {
            csvLabel.classList.add('disabled'); // Add disabled class to grey out label
        } else {
            csvLabel.classList.remove('disabled'); // Remove disabled class
        }
    });


   //To send requst to frontend views to check if csv file is corrupted or not
    csvForm.addEventListener('submit', function(event) {
        // event.preventDefault(); // Prevent the form from submitting the traditional way
        validateForm()
        const formData = new FormData(csvForm);
        
        fetch(csvForm.action, {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{csrfToken}}' // Include CSRF token
            },
            body: formData,
        })
        .then(response => {
            console.log(response);
            return response.json(); // Parse JSON from the response
        })
        .then(data => {
            console.log(data.message);
            // Handle the JSON response
            if (data.error) {
                let error = document.getElementById("error-message");
                console.log(error);
                error.textContent = data.error; // Display error message
            } else {
                submitButtonCSV.textContent = 'Uploaded'; // Change button text
                submitButtonCSV.disabled = true; // Optionally disable button
                submitButtonExcel.disabled = true; // Optionally disable button

                let success = document.getElementById("success-message");
                success.textContent = data.message; // Display success message
                // inputPrompt.textContent = data.csv_content;
                csvContent = data.csv_content;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.querySelector('p[style="color: red"]').textContent = 'An error occurred. Please try again.'; // Display a generic error message
        });
    });

    //To send requst to frontend views to check if excel file is corrupted or not
    excelForm.addEventListener('submit', function(event) {
        // event.preventDefault(); // Prevent the form from submitting the traditional way
        validateForm()
        const formData = new FormData(excelForm);
        
        fetch(excelForm.action, {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{csrfToken}}'
            },
            body: formData,
        })
        .then(response => {
            console.log(response);
            return response.json(); // Parse JSON from the response
        })
        .then(data => {
            console.log(data.message);
            // Handle the JSON response
            if (data.error) {
                let error = document.getElementById("error-message");
                console.log(error);
                error.textContent = data.error; // Display error message
            } else {
                submitButtonExcel.textContent = 'Uploaded'; // Change button text
                submitButtonExcel.disabled = true; // Optionally disable button
                submitButtonCSV.disabled = true; // Optionally disable button

                let success = document.getElementById("success-message");
                success.textContent = data.message; // Display success message
                excelContent  = data.excel_content;
                // inputPrompt.textContent = data.excel_content;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.querySelector('p[style="color: red"]').textContent = 'An error occurred. Please try again.'; // Display a generic error message
        });
    });
    
    generateForm.addEventListener('submit', function(event){
        const validatedData = validateInputs();
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value; // Extract CSRF token
        if(validatedData){
            const data = {
                username: sessionStorage.getItem('username'),
                database: validatedData['database'],
                prompt: validatedData['prompt'],
                fileUploaded: document.getElementById('csv-file').files.length > 0 ? csvContent : excelContent
            };
            console.log(data);
            fetch(generateForm.action,{ 
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            })
            .then(response => {
                console.log(response);
                return response.json(); // Parse JSON from the response
            })
            .then(data => {
                console.log(data.message);
                // Handle the JSON response
                if (data.error) {
                    let error = document.getElementById("error-message");
                    console.log(error);
                    error.textContent = data.error; // Display error message
                } else {
                   
                    let success = document.getElementById("success-message");
                    success.textContent = data.message; // Display success message
                    // inputPrompt.textContent = data.excel_content;
                    generatedContent.textContent = data.sql_generated;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.querySelector('p[style="color: red"]').textContent = 'An error occurred. Please try again.'; // Display a generic error message
            }); 
        }
    })


    inputPrompt.addEventListener('focus', function() {
        if (this.disabled) {
            alert("Please select a SQL Server and upload a file before entering text."); // Show alert if textarea is disabled
            this.blur(); // Remove focus to prevent typing
        }
    });
});

// To copy generated text to clipboard
function copyToClipboard(textareaId) {
    const textarea = document.getElementById(textareaId);
    textarea.select();
    document.execCommand("copy");
    alert("Copied to clipboard!"); // Optional: alert message
}

//To check if file uploaded for csv is of correct format and size
function validateCSVFile(input) {
    const file = input.files[0];
    const maxSize = 5 * 1024 * 1024; 
    console.log("hello");
    console.log(file);
    if (file && !file.name.endsWith('.csv')) {
        alert('Invalid file format. Only CSV files are allowed.');
        input.value = ''; // Clear the input
    }
    if (file.size > maxSize) {
        alert('File size exceeds 5 MB. Please upload a smaller file.');
        input.value = ''; // Clear the input if the file is too large
        return;
    }
    console.log("File is valid:", file.name);
}

//To check if file uploaded for excel is of correct format and size
function validateExcelFile(input) {
    const file = input.files[0];
    const maxSize = 5 * 1024 * 1024; 
    if (file && !file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
        alert('Invalid file format. Only Excel files are allowed.');
        input.value = ''; // Clear the input
    }
    if (file.size > maxSize) {
        alert('File size exceeds 5 MB. Please upload a smaller file.');
        input.value = ''; // Clear the input if the file is too large
        return;
    }
    console.log("File is valid:", file.name, file.size);
}

//To check if file is uploaded before submitting
function validateForm() {
    const csvInput = document.getElementById('csv-file');
    const excelInput = document.getElementById('excel-file');
    
    // Check if a file is selected
    if (csvInput.files.length > 0 || excelInput.files.length > 0) {
        return true;
    }
    else{
        alert('Please select a file before submitting.');
        event.preventDefault(); 
        return false;
    }
    
}

//To change the login and logout status after logging out
function changeSessionStatus(){
    sessionStorage.setItem('loggedOut', 'True')
    sessionStorage.setItem('isLoggedIn', 'False')
}


//Validate inputs while clicking on generate query button
function validateInputs() {

    const databaseSelect = document.getElementById('database-select');
    const csvFileInput = document.getElementById('csv-file');
    const excelFileInput = document.getElementById('excel-file');
    const inputPrompt = document.getElementById('prompt');

    const isDatabaseSelected = databaseSelect.value !== '';
    const isFileUploaded = csvFileInput.files.length > 0 || excelFileInput.files.length > 0;
    const isPromptEntered = inputPrompt.value.trim().length > 0;
    if(isFileUploaded){
        console.log("File uploaded");
        let submitStatus = document.getElementById("csv-button").textContent == "Uploaded" || document.getElementById("excel-button").textContent == "Uploaded" ;
        console.log(submitStatus);
        if(!isDatabaseSelected && submitStatus){
           alert("Please select SQL Server");
        }
        else if(!submitStatus){
            alert('Please submit the file.');
        }
        else if(!isPromptEntered) {
            alert('Please enter a prompt before generating the query.');
        }
        else{
            alert('Success');
            return {  // Return the valid data
                database: databaseSelect.value,
                prompt: inputPrompt.value.trim()
            };
        }
    }
    else{
        if(!isDatabaseSelected){
            alert("Please select SQL Server");
        }
         else if(!isPromptEntered) {
             alert('Please enter a prompt before generating the query.');
         }
         else{
            alert('Success');
            return {  // Return the valid data
                database: databaseSelect.value,
                prompt: inputPrompt.value.trim()
            };
            // sendGenerateRequestToView(databaseSelect, )
         }
    }

    
}


// function handleFormSubmit(event, form) {
//     event.preventDefault(); // Prevent default form submission

//     // Validate the form before proceeding
//     const isValid = validateForm();
//     if (!isValid) {
//         return; // Exit if the form is invalid
//     }

//     const submitButton = form.querySelector('button[type="submit"]');
//     submitButton.textContent = 'Uploaded'; // Change button text
//     submitButton.disabled = true; // Optionally disable button

//     // Optionally, you can send the form data using AJAX
//     const formData = new FormData(form);

//     // fetch(form.action, {
//     //     method: 'POST',
//     //     body: formData,
//     //     headers: {
//     //         'X-CSRFToken': '{{ csrf_token }}' // Include CSRF token
//     //     }
//     // })
//     // .then(response => response.json())
//     // .then(data => {
//     //     console.log(data);
//     //     // You can show a success message or update the UI accordingly
//     // })
//     // .catch(error => {
//     //     console.error('Error:', error);
//     //     // Optionally, reset the button text if submission fails
//     //     submitButton.textContent = 'Submit';
//     //     submitButton.disabled = false;
//     // });
//     fetch(csvForm.action, {
//         method: 'POST',
//         headers: {
//             'X-CSRFToken': csrfToken // Include CSRF token
//         },
//         body: formData,
//     })
//     .then(response => response.json())
//     .then(data => {
//         // Update the page with the response data
//         if (data.error) {
//             document.querySelector('p[style="color: red"]').textContent = data.error; // Display error message
//         } else {
//             document.querySelector('p[style="color: black"]').textContent = data.message; // Display success message
//             // If you want to display csv_content, you can do that here as well
//             console.log(data.csv_content); // Use this to update the page as needed
//         }
//     })
//     .catch(error => {
//         console.error('Error:', error);
//     });
// }


const generateBtn = document.getElementById('generate-btn');


function generateQuery() {
    const sqlType = document.getElementById('sql-type').value;
    const prompt = document.getElementById('prompt-input').value;
    let query = '';

    if (prompt.toLowerCase().includes('highest paid employee')) {
        query = `SELECT * FROM employees WHERE salary = (SELECT MAX(salary) FROM employees);`;
    } else {
        query = `-- SQL query for ${sqlType} based on prompt: ${prompt}`;
    }

    document.getElementById('generated-output').innerText = query;

    // Create a new textbox
    const newTextbox = document.createElement('textarea');
    newTextbox.rows = 4;
    newTextbox.style.width = '100%';
    newTextbox.style.border = 'none';
    newTextbox.style.outline = 'none';
    newTextbox.style.resize = 'none';
    newTextbox.style.fontSize = '24px';
    newTextbox.style.fontFamily = "'Inria Sans', sans-serif";
    newTextbox.style.color = '#808080';
    newTextbox.value = query;

    // Append the new textbox to the container
    const container = document.querySelector('.main-content');
    container.appendChild(newTextbox);
}