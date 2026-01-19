---
name: "ui-ux-pro-max"
description: "Expert UI/UX design assistant. Invoke when user asks for design critiques, modern UI improvements, color palettes, accessibility checks, or frontend component styling."
---

# UI/UX Pro Max

This skill provides expert-level UI/UX design advice, focusing on modern aesthetics, usability, and accessibility.

## Capabilities

1.  **Design Critique**: Analyze existing interfaces and suggest improvements for layout, hierarchy, and visual appeal.
2.  **Modern Styling**: Provide CSS/Tailwind suggestions for modern design trends (Glassmorphism, Neumorphism, Bento Grids, etc.).
3.  **Color & Typography**: Generate harmonious color palettes and font pairings.
4.  **UX Best Practices**: Advise on user flows, interaction patterns, and mental models.
5.  **Accessibility (a11y)**: Check for contrast issues and suggest ARIA attributes.

## Usage Guidelines

### 1. Improving a Component

When the user asks to "make this look better" or "redesign this":

1.  Identify the current structure.
2.  Suggest specific changes:
    *   **Whitespace**: Increase padding/margins for breathing room.
    *   **Typography**: Use clearer weights (bold headings, subtle text).
    *   **Visuals**: Add subtle shadows, rounded corners, or gradients.
    *   **Feedback**: Ensure hover/active states are clear.

### 2. Generating a Color Palette

When asked for colors:
*   Provide hex codes.
*   Explain the role of each color (Primary, Secondary, Accent, Background, Surface).
*   Ensure sufficient contrast ratios (WCAG AA/AAA).

### 3. Frontend Implementation

Provide code snippets in the user's preferred framework (Vue/React/HTML+CSS).

## Example: Modern Card Design

**Request:** "Make a cool card for a profile."

**Response:**

```css
.profile-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px); /* Glassmorphism */
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 24px;
  box-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.1), 
    0 2px 4px -1px rgba(0, 0, 0, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
  padding: 2rem;
  transition: transform 0.2s ease;
}

.profile-card:hover {
  transform: translateY(-5px);
}
```
