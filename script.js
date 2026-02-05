document.addEventListener('DOMContentLoaded', () => {
    console.log('KSRTC Dashboard Initialized');

    // Update live time
    function updateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { hour12: false });
        const timeElement = document.getElementById('current-time');
        if (timeElement) {
            timeElement.textContent = timeString;
        }
    }

    setInterval(updateTime, 1000);
    updateTime();

    // Initialize EPKM Chart
    const ctx = document.getElementById('epkmChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
                datasets: [{
                    label: 'EPKM Trend',
                    data: [42, 44, 30, 41, 43], // Matches the visual dip in Wed
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.05)',
                    borderWidth: 3,
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: '#0d6efd',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#e9ecef',
                            borderDash: [5, 5]
                        },
                        ticks: {
                            callback: function (value) {
                                return '₹' + value;
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // Default Date Inputs to Today
    const today = new Date().toISOString().split('T')[0];
    const searchDateInput = document.getElementById('searchDate');
    if (searchDateInput) searchDateInput.value = today;

    // Update Master Log Date Label
    const masterLogDate = document.getElementById('masterLogDate');
    if (masterLogDate) {
        const dateOptions = { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' };
        masterLogDate.textContent = new Date().toLocaleDateString('en-US', dateOptions);
    }

    // Search Form Logic
    const searchForm = document.getElementById('searchForm');
    const searchResults = document.getElementById('searchResults');

    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            // Simulate loading or filtering
            const btn = searchForm.querySelector('button');
            const originalText = btn.innerHTML;

            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Searching...';
            btn.disabled = true;

            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
                if (searchResults) {
                    searchResults.classList.remove('d-none');
                }
            }, 800);
        });
    }

    // Authentication Logic
    const AUTH_KEY = 'ksrtc_sm_session';

    function checkAuth() {
        const session = sessionStorage.getItem(AUTH_KEY);
        const isLoginPage = window.location.pathname.includes('login.html');

        if (!session && !isLoginPage) {
            window.location.href = 'login.html';
        } else if (session && isLoginPage) {
            window.location.href = 'index.html';
        }

        // Update Depot Display if on index page
        if (session && !isLoginPage) {
            const data = JSON.parse(session);
            const depotDisplay = document.getElementById('depot-display');
            if (depotDisplay && data.depotId) {
                // Map codes to names (simple mapping for demo)
                const depotNames = {
                    'TVM': 'Thiruvananthapuram Central',
                    'KML': 'Kumily',
                    'ALP': 'Alappuzha',
                    'KTYM': 'Kottayam',
                    'ERS': 'Ernakulam',
                    'TSR': 'Thrissur',
                    'PGT': 'Palakkad',
                    'KKD': 'Kozhikode',
                    'KNR': 'Kannur',
                    'KGD': 'Kasaragod',
                    'OTHER': 'Other Depot'
                };
                const name = depotNames[data.depotId] || data.depotId;
                depotDisplay.textContent = `Depot: ${name} (${data.stationMasterId})`;
            }
        }
    }

    // Run basic auth check on load
    if (!window.location.pathname.includes('login.html')) {
        checkAuth();
    }

    // Logout Handler
    window.logout = function () {
        sessionStorage.removeItem(AUTH_KEY);
        window.location.href = 'login.html';
    };

    // Attach logout to any logout buttons if they exist
    document.addEventListener('click', (e) => {
        const logoutBtn = e.target.closest('#logoutBtn');
        if (logoutBtn) {
            e.preventDefault();
            logout();
        }
    });
    // Live Sequence Tracker Search
    const liveTrackerSearchInput = document.getElementById('liveTrackerSearchInput');
    if (liveTrackerSearchInput) {
        liveTrackerSearchInput.addEventListener('keyup', function() {
            const filter = this.value.toUpperCase();
            const table = document.getElementById('liveTrackerTable');
            const tr = table.getElementsByTagName('tr');

            for (let i = 1; i < tr.length; i++) { // Start from 1 to skip header
                let displayed = false;
                // Search in Bus Number (index 0) and Current Depo (index 8)
                // Adjust indices if needed. 
                // Based on index.html:
                // 0: Bus Number (td class ps-4)
                // 8: Current Depo
                
                const tdBusNo = tr[i].getElementsByTagName('td')[0];
                const tdDepo = tr[i].getElementsByTagName('td')[8];

                if (tdBusNo || tdDepo) {
                    const txtBusNo = tdBusNo.textContent || tdBusNo.innerText;
                    const txtDepo = tdDepo ? (tdDepo.textContent || tdDepo.innerText) : "";
                    
                    if (txtBusNo.toUpperCase().indexOf(filter) > -1 || txtDepo.toUpperCase().indexOf(filter) > -1) {
                        tr[i].style.display = "";
                    } else {
                        tr[i].style.display = "none";
                    }
                }
            }
        });
    }
});

// Login Handler (outside DOMContentLoaded to ensure it runs if script is loaded differently, 
// though strictly it should be inside. But for login.html which might not have all the index structure...)
// Actually better keep it separate or check if element exists.

const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const depotId = document.getElementById('depotId').value;
        const stationMasterId = document.getElementById('stationMasterId').value;
        // Password would be validated here in a real app

        if (depotId && stationMasterId) {
            const sessionData = {
                depotId: depotId,
                stationMasterId: stationMasterId,
                loginTime: new Date().toISOString()
            };
            const AUTH_KEY = 'ksrtc_sm_session'; // Re-declare or scope properly

            sessionStorage.setItem(AUTH_KEY, JSON.stringify(sessionData));

            // Show success state
            const btn = loginForm.querySelector('button[type="submit"]');
            btn.innerHTML = '<i class="bi bi-check-circle me-2"></i>Success!';
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-success');

            setTimeout(() => {
                window.location.href = 'index.html';
            }, 500);
        }
    });
}
