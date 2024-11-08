// Connect to Socket.IO
const socket = io();

// Handle connection message
socket.on('connect', () => {
    console.log('Socket.IO connected');
});

// Initialize pagination variables for user data
let currentPage = 1;
const itemsPerPage = 5;  // Adjust this as needed
let totalPages = 1; // Default value until user data is received
let userData = []; // To store the current user data
let filteredData = []; // To store filtered data based on the search bar

// Initialize pagination variables for recent logins
let currentLoginPage = 1;
const loginsPerPage = 5;  // Limit of 5 logins per page
let totalLoginPages = 1;  // Default value until login events are received
let loginEvents = [];  // Store recent login data
let filteredLoginData = [];  // Store filtered login data

// Update pagination button and table for user data
function updatePagination() {
    const prevPageNum = document.getElementById("prevPageNum");
    const nextPageNum = document.getElementById("nextPageNum");

    // Update the page numbers on the buttons
    prevPageNum.textContent = currentPage;
    nextPageNum.textContent = currentPage + 1;

    // Disable the buttons if on the first or last page
    document.getElementById("prevBtn").disabled = currentPage === 1;
    document.getElementById("nextBtn").disabled = currentPage === totalPages;

    updateTable();
}

// Function to update the table for user data based on the current page
function updateTable() {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    
    const paginatedData = filteredData.slice(startIndex, endIndex); // Get data for the current page

    const userDataBody = document.getElementById('userDataBody');
    userDataBody.innerHTML = ''; // Clear current data

    // Populate with paginated data
    paginatedData.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(Date.parse(item.timestamp)).toLocaleString()}</td>
            <td>${item.ip}</td>
            <td>${item.packet_size}</td>
            <td>${item.request_rate}</td>
            <td>${item.label}</td>
        `;
        userDataBody.appendChild(row);
    });
}

// Receive real-time user data update from the server
socket.on('update_user_data', (data) => {
    console.log("Updating user data with:", data); // Log the data received
    userData = data; // Store the updated user data
    filteredData = userData; // Initialize filtered data with all user data
    totalPages = Math.ceil(filteredData.length / itemsPerPage); // Recalculate total pages
    currentPage = 1; // Reset to first page on new data
    updatePagination(); // Update the table and pagination buttons
});

// Update recent logins table in real-time
socket.on('update_recent_logins', (loginEventsReceived) => {
    console.log("Updating recent logins with:", loginEventsReceived);
    loginEvents = loginEventsReceived;  // Store the login events
    filteredLoginData = loginEvents;  // Initialize filtered data with all login events
    totalLoginPages = Math.ceil(filteredLoginData.length / loginsPerPage);  // Recalculate total pages
    currentLoginPage = 1;  // Reset to first page on new data
    updateLoginPagination();  // Update the table and pagination buttons
});

// Update pagination button and table for recent logins
function updateLoginPagination() {
    const prevLoginPageNum = document.getElementById("prevLoginPageNum");
    const nextLoginPageNum = document.getElementById("nextLoginPageNum");

    // Update the page numbers on the buttons
    prevLoginPageNum.textContent = currentLoginPage;
    nextLoginPageNum.textContent = currentLoginPage + 1;

    // Disable the buttons if on the first or last page
    document.getElementById("prevLoginBtn").disabled = currentLoginPage === 1;
    document.getElementById("nextLoginBtn").disabled = currentLoginPage === totalLoginPages;

    updateLoginTable();
}

// Function to update the table for recent logins based on the current page
function updateLoginTable() {
    const startIndex = (currentLoginPage - 1) * loginsPerPage;
    const endIndex = startIndex + loginsPerPage;
    
    const paginatedLoginData = filteredLoginData.slice(startIndex, endIndex);  // Get data for the current page

    const recentLoginsBody = document.querySelector('.recent-logins tbody');
    recentLoginsBody.innerHTML = '';  // Clear current logins

    // Populate with paginated data
    paginatedLoginData.forEach(event => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${event.email}</td>
            <td>${event.username}</td>
            <td>${new Date(event.timestamp * 1000).toLocaleString()}</td> <!-- Convert timestamp -->
        `;
        recentLoginsBody.appendChild(row);
    });
}

// Event listeners for sidebar and dark mode toggle
const sideMenu = document.querySelector('aside');
const menuBtn = document.getElementById('menu-btn');
const closeBtn = document.getElementById('close-btn');
const darkMode = document.querySelector('.dark-mode');

menuBtn.addEventListener('click', () => {
    sideMenu.style.display = 'block';
});

closeBtn.addEventListener('click', () => {
    sideMenu.style.display = 'none';
});

darkMode.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode-variables');
    darkMode.querySelector('span:nth-child(1)').classList.toggle('active');
    darkMode.querySelector('span:nth-child(2)').classList.toggle('active');
});

// Function to filter table by label or IP address
function filterTable() {
    const input = document.getElementById("labelSearch").value.toUpperCase();
    
    // Filter the userData based on the input search value for label or IP address
    filteredData = userData.filter(item => {
        return (
            item.label.toUpperCase().includes(input) ||  // Match label
            item.ip.toUpperCase().includes(input)        // Match IP address
        );
    });

    currentPage = 1;  // Reset to first page when new filter is applied
    totalPages = Math.ceil(filteredData.length / itemsPerPage); // Recalculate total pages
    updatePagination(); // Update the table and pagination buttons
}



// Listen for new attack events
socket.on('new_attack', (attackEvent) => {
    console.log("New attack event received:", attackEvent);  // Debugging log

    // Add the new attack event to the userData array
    userData.push(attackEvent);

    // Reapply the current filter
    filteredData = userData.filter(item => {
        return item.label.toUpperCase().includes(document.getElementById('labelSearch').value.toUpperCase());
    });

    // Recalculate total pages and update the pagination
    totalPages = Math.ceil(filteredData.length / itemsPerPage);
    updatePagination(); // Update pagination and table
});

// Handle disconnect event
socket.on('disconnect', () => {
    console.log('Disconnected from server');
});

// Initialize event listeners on DOM content load
document.addEventListener('DOMContentLoaded', () => {
    // Attach the filter function to the search input
    const labelSearchInput = document.getElementById('labelSearch');
    labelSearchInput.addEventListener('keyup', filterTable);

    // Pagination event listeners for user data
    document.getElementById('prevBtn').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            updatePagination();
        }
    });

document.addEventListener('DOMContentLoaded', () => {
        // Fetch initial attack data from the server
        fetch('/get_attack_data')
            .then(response => response.json())
            .then(data => {
                console.log("Data received from /get_attack_data:", data); // Debugging
                userData = data;
                filteredData = userData; // Initialize filtered data
                totalPages = Math.ceil(filteredData.length / itemsPerPage);
                currentPage = 1; // Reset to the first page
                updatePagination(); // Update the table and pagination buttons
            })
            .catch(error => console.error("Error fetching attack data:", error));
    });
    

    document.getElementById('nextBtn').addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            updatePagination();
        }
    });

    // Pagination event listeners for recent logins
    document.getElementById('prevLoginBtn').addEventListener('click', () => {
        if (currentLoginPage > 1) {
            currentLoginPage--;
            updateLoginPagination();
        }
    });

    document.getElementById('nextLoginBtn').addEventListener('click', () => {
        if (currentLoginPage < totalLoginPages) {
            currentLoginPage++;
            updateLoginPagination();
        }
    });
});
