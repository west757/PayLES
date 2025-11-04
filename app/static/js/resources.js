// --- Resource Metadata ---
const RESOURCE_CATEGORIES = [
	{ key: 'General', label: 'General' },
	{ key: 'Financial', label: 'Financial' },
	{ key: 'PCS/Moving', label: 'PCS/Moving' },
	{ key: 'Travel', label: 'Travel' },
	{ key: 'Education', label: 'Education' },
	{ key: 'Health', label: 'Health' },
    { key: 'Legal', label: 'Legal' },
	{ key: 'Resource List', label: 'Resource List' },
	{ key: 'Calculator', label: 'Calculator' },
];
const RESOURCE_BRANCHES = [
	{ key: 'DoD', label: 'DoD' },
    { key: 'U.S. Army', label: 'U.S. Army' },
	{ key: 'U.S. Air Force', label: 'U.S. Air Force' },
	{ key: 'U.S. Space Force', label: 'U.S. Space Force' },
	{ key: 'U.S. Navy', label: 'U.S. Navy' },
	{ key: 'U.S. Marine Corps', label: 'U.S. Marine Corps' },
    { key: 'Non-DoD', label: 'Non-DoD' },
];

// --- Utility: Star Icon SVG ---
function getStarIcon() {
	return `<span class="resource-featured-star" title="Featured Resource">★</span>`;
}

async function fetchAndFlattenResources() {
    // Fetch the JSON file
    const resp = await fetch('/static/json/resources.json');
    const data = await resp.json();
    // data is already a flat array of resources
    // Ensure category and branch are strings, and featured is boolean
    let flat = data.map(item => ({
        ...item,
        category: typeof item.category === 'string' ? item.category : '',
        branch: typeof item.branch === 'string' ? item.branch : '',
        featured: !!item.featured,
    }));
    // Sort alphabetically by name
    flat.sort((a, b) => a.name.localeCompare(b.name));
    return flat;
}

// --- Render Category and Branch Filters ---
function renderCategoryFilters(selected) {
	const container = document.getElementById('resources-category-filters');
	container.innerHTML = '';
	RESOURCE_CATEGORIES.forEach(cat => {
		const id = `cat-filter-${cat.key}`;
		const checked = selected.includes(cat.key) ? 'checked' : '';
		container.innerHTML += `
			<label class="resources-filter-label" for="${id}">
				<input type="checkbox" class="resources-filter-checkbox" id="${id}" value="${cat.key}" ${checked} />
				${cat.label}
			</label>
		`;
	});
}

function renderBranchFilters(selected) {
	const container = document.getElementById('resources-branch-filters');
	container.innerHTML = '';
	RESOURCE_BRANCHES.forEach(branch => {
		const id = `branch-filter-${branch.key.replace(/\s/g, '-')}`;
		const checked = selected.includes(branch.key) ? 'checked' : '';
		container.innerHTML += `
			<label class="resources-filter-label" for="${id}">
				<input type="checkbox" class="resources-filter-checkbox" id="${id}" value="${branch.key}" ${checked} />
				${branch.label}
			</label>
		`;
	});
}

// --- Render Resource List ---
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
		return `
			<div class="resource-rect" tabindex="0" onclick="window.open('${resource.url}','_blank', 'noopener noreferrer')" title="${resource.name}">
				${star}
				<div class="resource-main">
					<div class="resource-name">${resource.name}</div>
					<div class="resource-desc">${resource.desc || ''}</div>
					<div class="resource-meta">${cats}${branches}</div>
				</div>
			</div>
		`;
	}).join('')}</div>`;
}

window.initResourcesPage = async function initResourcesPage() {
    let allResources = await fetchAndFlattenResources();
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
                <input type="checkbox" class="resources-filter-checkbox" value="${opt.key}" ${selected.includes(opt.key) ? 'checked' : ''} data-type="${type}" />
                ${opt.label}
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
        let filtered = allResources;
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

    // Pagination logic
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

    // Initial render
    renderDropdownPanel('categories-dropdown-panel', RESOURCE_CATEGORIES, selectedCategories, 'category');
    renderDropdownPanel('branches-dropdown-panel', RESOURCE_BRANCHES, selectedBranches, 'branch');
    setupDropdown('categories-dropdown-btn', 'categories-dropdown-panel');
    setupDropdown('branches-dropdown-btn', 'branches-dropdown-panel');
    updateResourceList();
};