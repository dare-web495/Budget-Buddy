function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === ('csrftoken=')) {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}


const shillingFormatter = new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES',
    minimumFractionDigits: 2
});


async function initiateAccountTermination() {
    const confirmation = confirm("CRITICAL WARNING: Are you absolutely certain you want to close your account? This action deletes all historical income records, transactions, and budget data permanently.");
    
    if (!confirmation) return;

    try {
        const response = await fetch('/api/account/delete/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        });

        const data = await response.json();
        
        if (data.status === 'success') {
            window.location.href = data.redirect_url;
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (error) {
        console.error("Network communication error:", error);
        alert("Unable to process account deletion at this moment.");
    }
}


document.addEventListener("DOMContentLoaded", () => {
    
    const incomeForm = document.getElementById("income-pool-form");
    if (incomeForm) {
        incomeForm.addEventListener("submit", async (e) => {
            e.preventDefault(); 

            const payload = {
                source: document.getElementById("input-source").value,
                amount: parseFloat(document.getElementById("input-amount").value)
            };

            try {
                const response = await fetch("/finance/income/add/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken() 
                    },
                    body: JSON.stringify(payload)
                });
                
                const data = await response.json();
                if (data.status === "success") {
                    window.location.reload();
                } else {
                    alert(`System Error: ${data.message}`);
                }
            } catch (err) {
                console.error("Communication failure:", err);
            }
        });
    }

    const allocationForm = document.getElementById("allocation-form");
    if (allocationForm) {
        allocationForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const payload = {
                category: document.getElementById("alloc-category").value,
                description: document.getElementById("alloc-description").value,
                amount: parseFloat(document.getElementById("alloc-amount").value)
            };

            try {
                const response = await fetch("/finance/allocation/add/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken()
                    },
                    body: JSON.stringify(payload)
                });
                
                const data = await response.json();
                if (data.status === "success") {
                    bootstrap.Modal.getInstance(document.getElementById("allocationModal")).hide();
                    allocationForm.reset();
                    updateDashboardData(); 
                } else {
                    alert(`Error: ${data.message}`);
                    console.log(`Error:${data.error}`);
                }
            } catch (err) {
                console.error(err);
            }
        });
    }

    const transactionForm = document.getElementById("transaction-form");
    if (transactionForm) {
        transactionForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const payload = {
                category: document.getElementById("trans-category").value,
                description: document.getElementById("trans-description").value,
                amount: parseFloat(document.getElementById("trans-amount").value)
            };

            try {
                const response = await fetch("/finance/transaction/add/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken()
                    },
                    body: JSON.stringify(payload)
                });
                
                const data = await response.json();
                if (data.status === "success") {
                    bootstrap.Modal.getInstance(document.getElementById("transactionModal")).hide();
                    transactionForm.reset();
                    updateDashboardData()
                } else {
                    alert(`Error: ${data.message}`);
                }
            } catch (err) {
                console.error(err);
            }
        });
    }

    if (document.getElementById("metric-income")) {
        updateDashboardData();
    }
});


async function updateDashboardData() {
    const today = new Date();

    try {
        const response = await fetch(`/finance/summary/${today.getFullYear()}/${today.getMonth() + 1}/`);
        const data = await response.json();

        // Map live numbers into metric cards
        document.getElementById("metric-income").innerText = shillingFormatter.format(data.total_income);
        document.getElementById("metric-spent").innerText = shillingFormatter.format(data.total_actual_spent);
        document.getElementById("metric-saved").innerText = shillingFormatter.format(data.total_actual_saved);
        
        const container = document.getElementById("allocation-container");
        container.innerHTML = "";
        
        const transCategoryDropdown = document.getElementById("trans-category");
        if (transCategoryDropdown) {
            transCategoryDropdown.innerHTML = '<option value="" selected disabled>Choose an envelope...</option>';
        }

        let totalAllocated = 0;
        let visibleEnvelopesCount = 0;

        if (Object.keys(data.category_comparison).length === 0) {
            container.innerHTML = '<div class="text-center text-muted small opacity-50 py-3">No envelope allocations configured.</div>';
            if (transCategoryDropdown) {
                transCategoryDropdown.innerHTML = '<option value="" selected disabled>No envelopes available. Create one first!</option>';
            }
        } else {
            for (const [name, stats] of Object.entries(data.category_comparison)) {
                totalAllocated += stats.allocated;
                
                const percent = stats.allocated > 0 ? (stats.spent / stats.allocated) * 100 : 0;

                if (percent >= 100) {
                    if (!sessionStorage.getItem(`alerted-${name}`)) {
                        alert(`Notification: Your "${name}" envelope allocation is fully utilized (KES ${shillingFormatter.format(stats.spent)} of KES ${shillingFormatter.format(stats.allocated)} spent). It will now be archived from your active dashboard card.`);
                        sessionStorage.setItem(`alerted-${name}`, "true");
                    }
                    continue; 
                }

                visibleEnvelopesCount++;

                const barColor = percent >= 90 ? "bg-danger" : percent >= 70 ? "bg-warning" : "bg-success";
                
                container.innerHTML += `
                    <div>
                        <div class="d-flex justify-content-between small mb-1">
                            <span class="fw-bold">${name}</span>
                            <span class="text-muted">${shillingFormatter.format(stats.spent)} / ${shillingFormatter.format(stats.allocated)}</span>
                        </div>
                        <div class="progress" style="height: 8px;">
                            <div class="progress-bar ${barColor}" role="progressbar" style="width: ${Math.min(percent, 100)}%"></div>
                        </div>
                    </div>
                `;

                if (transCategoryDropdown) {
                    transCategoryDropdown.innerHTML += `<option value="${name}">${name}</option>`;
                }
            }

            if (visibleEnvelopesCount === 0 && Object.keys(data.category_comparison).length > 0) {
                container.innerHTML = '<div class="text-center text-success small fw-semibold py-3"><i class="bi bi-check-circle-fill me-2"></i>All budget envelopes successfully completed!</div>';
            }
        }

        document.getElementById("metric-allocated").innerText = shillingFormatter.format(totalAllocated);
        document.getElementById("metric-unallocated-text").innerText = `${shillingFormatter.format(data.total_income - totalAllocated)} left to plan`;

        // Render Recent Transactions Ledger Table
        const ledgerBody = document.getElementById("transaction-ledger-body");
        ledgerBody.innerHTML = "";

        if (!data.recent_transactions || data.recent_transactions.length === 0) {
            ledgerBody.innerHTML = '<tr><td colspan="4" class="text-center py-4 text-muted opacity-75">No recorded spending actions found this month.</td></tr>';
        } else {
            data.recent_transactions.forEach(tx => {
                let badgeColor = tx.category === "EXPENSE" ? "bg-danger" : tx.category === "WANT" ? "bg-warning text-dark" : "bg-success";
                
                ledgerBody.innerHTML += `
                    <tr>
                        <td class="fw-semibold text-dark">${tx.description}</td>
                        <td><span class="badge ${badgeColor}">${tx.category}</span></td>
                        <td class="fw-bold text-dark">${shillingFormatter.format(tx.amount)}</td>
                        <td class="text-end text-muted xsmall">${tx.action_time}</td>
                    </tr>
                `;
            });
        }

        // Dynamic Advisor Pipeline Engine
        const recContainer = document.getElementById("recommendations-container");
        recContainer.innerHTML = ""; 

        let recs = [];

        if (data.total_unallocated > 0) {
            recs.push({
                icon: "bi-lightning-charge-fill",
                color: "text-warning",
                title: "Idle Cash Detected",
                desc: `You have KES ${shillingFormatter.format(data.total_unallocated)} left to plan. Consider funding a flexible High-Yield Money Market Fund (MMF) like Cytonn, Sanlam, or Zimele to beat local inflation.`
            });
        }

        if (data.total_actual_saved > 0) {
            recs.push({
                icon: "bi-graph-up-arrow",
                color: "text-success",
                title: "Asset Allocation Match",
                desc: `Great job saving KES ${shillingFormatter.format(data.total_actual_saved)}! Look into stable infrastructure setups like Central Bank of Kenya (CBK) Treasury Bills, or retail bonds via M-Akiba.`
            });
        }

        const burnRate = data.total_income > 0 ? (data.total_actual_spent / data.total_income) * 100 : 0;
        if (burnRate > 70) {
            recs.push({
                icon: "bi-exclamation-triangle-fill",
                color: "text-danger",
                title: "High Burn Rate Warning",
                desc: `You have consumed ${burnRate.toFixed(0)}% of your master income pool. We suggest pausing unnecessary lifestyle 'WANT' transactions over the next few days to safeguard your liquidity.`
            });
        }

        if (recs.length === 0) {
            recs.push({
                icon: "bi-shield-check",
                color: "text-info",
                title: "Optimal Strategy Achieved",
                desc: "Your master pool is completely allocated and your current burn rate is balanced perfectly. Maintain your plan and keep logging transactions daily!"
            });
        }

        recs.forEach(rec => {
            recContainer.innerHTML += `
                <div class="p-3 rounded bg-secondary bg-opacity-25 border border-secondary border-opacity-50">
                    <div class="d-flex gap-2 align-items-center mb-1">
                        <i class="bi ${rec.icon} ${rec.color} fs-6"></i>
                        <h6 class="m-0 fw-bold text-light small">${rec.title}</h6>
                    </div>
                    <p class="text-light-50 m-0 xsmall lh-base">${rec.desc}</p>
                </div>
            `;
        });

    } catch (err) {
        console.error("Dashboard renderer broke down:", err);
    }
}
