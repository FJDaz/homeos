// Get the toggle button element
const toggleButton = document.querySelector('.toggle-button');

// Add event listener to the toggle button
toggleButton.addEventListener('click', () => {
  // Toggle the checked state of the checkbox
  toggleButton.querySelector('input').checked = !toggleButton.querySelector('input').checked;

  // Update the toggle button styles based on the checked state
  if (toggleButton.querySelector('input').checked) {
    toggleButton.classList.add('checked');
  } else {
    toggleButton.classList.remove('checked');
  }
});

// Initialize the toggle button styles
if (toggleButton.querySelector('input').checked) {
  toggleButton.classList.add('checked');
}

// Make the toggle button accessible
toggleButton.setAttribute('role', 'button');
toggleButton.setAttribute('aria-pressed', 'false');
toggleButton.querySelector('input').setAttribute('aria-hidden', 'true');

// Update the aria-pressed attribute based on the checked state
toggleButton.addEventListener('click', () => {
  if (toggleButton.querySelector('input').checked) {
    toggleButton.setAttribute('aria-pressed', 'true');
  } else {
    toggleButton.setAttribute('aria-pressed', 'false');
  }
});

class AgentRouter:
    def select_agent(self, task: Task) -> Agent:
        decision_matrix = {
            "code_generation_large": {
                "agent": "deepseek_v3",
                "conditions": [
                    task.complexity > 0.7,
                    task.size_in_tokens > 500,
                    task.type in ["module_creation", "component_development"]
                ]
            },
            "code_generation_small": {
                "agent": "deepseek_v2",
                "conditions": [
                    task.complexity <= 0.7,
                    task.size_in_tokens <= 500,
                    task.type in ["bug_fixing", "minor_update"]
                ]
            }
        }

        for agent_type, conditions in decision_matrix.items():
            if all(condition for condition in conditions["conditions"]):
                return Agent(agent_type)

        # Default agent
        return Agent("default_agent")

/**
 * @fileoverview JavaScript for an accessible, performant, and ecological upload button component.
 * @version 1.0.0
 * @license MIT
 *
 * This script generates a vanilla JavaScript component for an upload button.
 * It focuses on performance by minimizing DOM manipulations and using efficient event handling.
 * Accessibility is ensured through proper ARIA attributes and interaction patterns.
 * The code is designed to be maintainable and follows best practices for a lean ecological footprint.
 */

/**
 * Creates and returns an accessible upload button component.
 * The component consists of a visually styled button and a hidden file input
 * that is programmatically triggered when the button is clicked.
 *
 * @returns {HTMLButtonElement} The button element that serves as the upload trigger.
 */
function createUploadButtonComponent() {
    // 1. Create the accessible button element
    const uploadButton = document.createElement('button');
    uploadButton.type = 'button'; // Ensures it's not a submit button by default
    uploadButton.className = 'upload-button'; // Applies the CSS class for styling
    // Provide a descriptive ARIA label for screen readers
    uploadButton.setAttribute('aria-label', 'Upload files from your device');

    // 2. Create the span for the button's visible text content
    const buttonTextSpan = document.createElement('span');
    buttonTextSpan.textContent = 'Upload';
    uploadButton.appendChild(buttonTextSpan);

    // 3. Create the hidden file input element
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.id = 'hiddenFileInput'; // Unique ID for potential programmatic access or labeling
    // Visually hide the input without using display: none, which can impact some screen readers.
    // Making it unfocusable via tabindex="-1" ensures the button is the sole interaction point.
    fileInput.style.position = 'absolute';
    fileInput.style.left = '-9999px';
    fileInput.style.width = '1px';
    fileInput.style.height = '1px';
    fileInput.style.overflow = 'hidden';
    fileInput.style.opacity = '0';
    fileInput.setAttribute('tabindex', '-1'); // Prevents direct keyboard focus on the hidden input

    // 4. Event Listeners for interaction and file handling

    /**
     * Handles the click event on the upload button.
     * Programmatically triggers a click on the hidden file input, opening the file selection dialog.
     * @param {Event} event The click event object.
     */
    const handleButtonClick = (event) => {
        // Prevent any default behavior if the button were part of a form, though type="button" handles this.
        event.preventDefault();
        fileInput.click(); // This opens the native file selection dialog
    };
    uploadButton.addEventListener('click', handleButtonClick);

    /**
     * Handles the change event on the hidden file input.
     * This event fires when the user has selected one or more files.
     * @param {Event} event The change event object, where event.target is the file input.
     */
    const handleFileChange = (event) => {
        const files = event.target.files; // Get the FileList object
        if (files.length > 0) {
            console.log(`Selected ${files.length} file(s):`);
            // Example: Iterate through selected files and log their names and sizes.
            // In a real application, this is where you'd initiate upload, display previews, etc.
            Array.from(files).forEach(file => {
                console.log(`- ${file.name} (Type: ${file.type || 'N/A'}, Size: ${(file.size / 1024).toFixed(2)} KB)`);
            });

            // Implement your file processing/upload logic here.
            // For performance and ecological footprint, process files efficiently:
            // - Use Web Workers for heavy processing to avoid blocking the main thread.
            // - Optimize image/video processing before upload if applicable.
            // - Send files in chunks if they are very large.
        } else {
            console.log('No files selected.');
        }
        // Important for allowing the user to select the same file(s) again
        // after cancelling or selecting, as the 'change' event only fires if the value changes.
        event.target.value = '';
    };
    fileInput.addEventListener('change', handleFileChange);

    // Append the hidden file input directly to the body or a root element.
    // Its visual position doesn't matter, and it's a helper for the button.
    document.body.appendChild(fileInput);

    // Return the visible button element, which will be centered by the CSS
    return uploadButton;
}

/**
 * Initializes the upload button component once the DOM is fully loaded.
 * This ensures all necessary elements are available before the script attempts to manipulate them.
 */
document.addEventListener('DOMContentLoaded', () => {
    // Create the upload button component
    const uploadButtonElement = createUploadButtonComponent();
    // Append the button to the document body.
    // The CSS provided in the previous step (for body and .upload-button) will handle centering.
    document.body.appendChild(uploadButtonElement);

    console.log('Upload button component successfully initialized and added to the DOM.');
});