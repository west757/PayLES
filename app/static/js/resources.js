const RESOURCE_CATEGORIES = [
    'General',
    'Financial',
    'PCS/Moving',
    'Travel',
    'Education',
    'Health',
    'Legal',
    'Resource List',
    'Calculator'
];
const RESOURCE_BRANCHES = [
    'DoD',
    'U.S. Army',
    'U.S. Air Force',
    'U.S. Space Force',
    'U.S. Navy',
    'U.S. Marine Corps',
    'Non-DoD'
];


function getStarIcon() {
	return `<span class="resource-featured-star" title="Featured Resource">★</span>`;
}


function renderCategoryFilters(selected) {
    const container = document.getElementById('resources-category-filters');
    container.innerHTML = '';
    RESOURCE_CATEGORIES.forEach(cat => {
        const id = `cat-filter-${cat.replace(/\s/g, '-')}`;
        const checked = selected.includes(cat) ? 'checked' : '';
        container.innerHTML += `
            <label class="resources-filter-label" for="${id}">
                <input type="checkbox" class="resources-filter-checkbox" id="${id}" value="${cat}" ${checked} />
                ${cat}
            </label>
        `;
    });
}


function renderBranchFilters(selected) {
    const container = document.getElementById('resources-branch-filters');
    container.innerHTML = '';
    RESOURCE_BRANCHES.forEach(branch => {
        const id = `branch-filter-${branch.replace(/\s/g, '-')}`;
        const checked = selected.includes(branch) ? 'checked' : '';
        container.innerHTML += `
            <label class="resources-filter-label" for="${id}">
                <input type="checkbox" class="resources-filter-checkbox" id="${id}" value="${branch}" ${checked} />
                ${branch}
            </label>
        `;
    });
}

function renderResourceList(resources) {
    const container = document.getElementById('resources-container');
    if (!resources.length) {
        container.innerHTML = '<div style="margin:2em 0;color:#888;">No resources found.</div>';
        return;
    }
    container.innerHTML = `<div class="resources-list">${resources.map(resource => {
        const star = resource.featured ? getStarIcon() : '';
        const cats = resource.category ? `<span class="resource-category-badge">${resource.category}</span>` : '';
        const branches = resource.branch ? `<span class="resource-branch-badge">${resource.branch}</span>` : '';
        const cac = resource.cac ? `<span class="resource-cac-badge">CAC Required</span>` : '';
        return `
            <div class="resource-rect" tabindex="0" onclick="window.open('${resource.url}','_blank', 'noopener noreferrer')" title="${resource.name}">
                <div class="resource-main">
                    <div class="resource-name">
                        ${star}
                        ${resource.name}
                    </div>
                    <div class="resource-desc">${resource.desc || ''}</div>
                    <div class="resource-meta">${cats}${branches}${cac}</div>
                </div>
            </div>
        `;
    }).join('')}</div>`;
}


window.initResourcesPage = async function initResourcesPage() {
    let RESOURCES = window.CONFIG.RESOURCES;
    let searchValue = '';
    let selectedCategories = [];
    let selectedBranches = [];
    let currentPage = 1;
    const pageSize = window.MAX_RESOURCES_DISPLAY || 20;

    // Render dropdown panels
    function renderDropdownPanel(panelId, options, selected, type) {
        const panel = document.getElementById(panelId);
        panel.innerHTML = options.map(opt => `
            <label class="resources-filter-label">
                <input type="checkbox" class="resources-filter-checkbox" value="${opt}" ${selected.includes(opt) ? 'checked' : ''} data-type="${type}" />
                ${opt}
            </label>
        `).join('');
    }

    // Toggle dropdowns
    function setupDropdown(btnId, panelId) {
        const btn = document.getElementById(btnId);
        const panel = document.getElementById(panelId);
        btn.addEventListener('click', () => {
            panel.classList.toggle('open');
        });
        document.addEventListener('click', (e) => {
            if (!btn.contains(e.target) && !panel.contains(e.target)) {
                panel.classList.remove('open');
            }
        });
    }

    // Filtering logic (same as before)
    function filterResources() {
        let filtered = RESOURCES;
        if (searchValue) {
            const sv = searchValue.toLowerCase();
            filtered = filtered.filter(r => r.name.toLowerCase().includes(sv));
        }
        if (selectedCategories.length) {
            filtered = filtered.filter(r =>
                selectedCategories.includes(r.category)
            );
        }
        if (selectedBranches.length) {
            filtered = filtered.filter(r =>
                selectedBranches.includes(r.branch)
            );
        }
        return filtered;
    }

    function renderPagination(total, page) {
        const container = document.getElementById('resources-pagination');
        const totalPages = Math.ceil(total / pageSize);
        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }
        container.innerHTML = '';
        for (let i = 1; i <= totalPages; i++) {
            container.innerHTML += `<button class="resources-pagination-btn${i === page ? ' active' : ''}" data-page="${i}">${i}</button>`;
        }
        container.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', () => {
                currentPage = parseInt(btn.getAttribute('data-page'));
                updateResourceList();
                // Scroll to top of the resources page
                const pageContainer = document.getElementById('page-resources');
                if (pageContainer) {
                    pageContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
    }

    // Render resource list for current page
    function updateResourceList() {
        const filtered = filterResources();
        const start = (currentPage - 1) * pageSize;
        const end = start + pageSize;
        renderResourceList(filtered.slice(start, end));
        renderPagination(filtered.length, currentPage);
        // Update resource count
        const countSpan = document.getElementById('resources-count');
        countSpan.textContent = `${filtered.length} Resource${filtered.length === 1 ? '' : 's'}`;
    }

    // Event listeners for search and filters
    document.getElementById('resources-search-bar').addEventListener('input', e => {
        searchValue = e.target.value.slice(0, 40);
        currentPage = 1;
        updateResourceList();
    });

    document.getElementById('categories-dropdown-panel').addEventListener('change', e => {
        if (e.target.classList.contains('resources-filter-checkbox')) {
            const val = e.target.value;
            if (e.target.checked) {
                if (!selectedCategories.includes(val)) selectedCategories.push(val);
            } else {
                selectedCategories = selectedCategories.filter(c => c !== val);
            }
            currentPage = 1;
            updateResourceList();
        }
    });

    document.getElementById('branches-dropdown-panel').addEventListener('change', e => {
        if (e.target.classList.contains('resources-filter-checkbox')) {
            const val = e.target.value;
            if (e.target.checked) {
                if (!selectedBranches.includes(val)) selectedBranches.push(val);
            } else {
                selectedBranches = selectedBranches.filter(b => b !== val);
            }
            currentPage = 1;
            updateResourceList();
        }
    });

    renderDropdownPanel('categories-dropdown-panel', RESOURCE_CATEGORIES, selectedCategories, 'category');
    renderDropdownPanel('branches-dropdown-panel', RESOURCE_BRANCHES, selectedBranches, 'branch');
    setupDropdown('categories-dropdown-btn', 'categories-dropdown-panel');
    setupDropdown('branches-dropdown-btn', 'branches-dropdown-panel');
    updateResourceList();
};