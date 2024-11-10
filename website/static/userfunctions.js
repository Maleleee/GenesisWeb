let sidebarOpen = false;
const sidebar = document.querySelector('.sidebar');
const sideMenu = document.querySelector('aside');
const menuBtn = document.getElementById('menu-btn');
const closeBtn = document.getElementById('close-btn');
const darkModeToggle = document.querySelector('.dark-mode');
const body = document.querySelector('body');
const lightModeIcon = darkModeToggle.querySelector('span:nth-child(1)'); // Light mode icon
const darkModeIcon = darkModeToggle.querySelector('span:nth-child(2)'); // Dark mode icon

// Function to open the sidebar
function openSidebar() {
  if (!sidebarOpen) {
    sidebar.classList.add('sidebar-responsive');
    sidebarOpen = true;
  }
}

// Function to close the sidebar
function closeSidebar() {
  if (sidebarOpen) {
    sidebar.classList.remove('sidebar-responsive');
    sidebarOpen = false;
  }
}

// Event listeners for sidebar toggle
menuBtn.addEventListener('click', openSidebar);
closeBtn.addEventListener('click', closeSidebar);

// Function to toggle dark mode
function toggleDarkMode() {
  body.classList.toggle('dark-mode');
  
  // Toggle active class on icons
  lightModeIcon.classList.toggle('active');
  darkModeIcon.classList.toggle('active');

  // Save user preference in a cookie
  document.cookie = `darkMode=${body.classList.contains('dark-mode') ? 'enabled' : 'disabled'}; path=/; max-age=31536000`; // 1 year
}

// Check for saved user preference on page load
function checkDarkModePreference() {
  const cookies = document.cookie.split('; ');
  const darkModeCookie = cookies.find(row => row.startsWith('darkMode='));
  
  if (darkModeCookie && darkModeCookie.split('=')[1] === 'enabled') {
    body.classList.add('dark-mode');
    // Set active class on icons
    lightModeIcon.classList.remove('active');
    darkModeIcon.classList.add('active');
  } else {
    // Ensure light mode is active if dark mode is not enabled
    body.classList.remove('dark-mode'); // Ensure light mode is set
    lightModeIcon.classList.add('active');
    darkModeIcon.classList.remove('active');
  }
}

// Event listener for dark mode toggle button
darkModeToggle.addEventListener('click', toggleDarkMode);

// Check dark mode preference on load
checkDarkModePreference();

function openWithdraw() {
  document.getElementById('withdrawModal').style.display = 'flex';
}

function closeWithdraw() {
  document.getElementById('withdrawModal').style.display = 'none';
}

function openDeposit() {
  document.getElementById('depositModal').style.display = 'flex';
}

function closeDeposit() {
  document.getElementById('depositModal').style.display = 'none';
}

function openTransactions() {
  document.getElementById('transactionsModal').style.display = 'flex';
}

function closeTransactions() {
  document.getElementById('transactionsModal').style.display = 'none';
}