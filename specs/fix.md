# Fix Error

**Objective**: Resolve the error in thrown before `analysis agents section should trigger`

Error: Company directory not found. Please process documents first.

I am getting the above error even when UI says:

```
Pitch Deck processed successfully!
Company: ZINIOSA
Output Directory: outputs/ziniosa
```

Could you please analyse the streamlit_app.py and and the previous pitch_deck_section() pipeline. Understand the flow and please find the root cause of this issue. Also, come up with solution strategy to resolve this issue. I will review and once we are both on the same page, we'll move to implmenetation. Please append this file with your findings and solution

## Analysis & Root Cause

### Application Flow Analysis

The Streamlit application follows this flow:
1. **Pitch Deck Upload** (`pitch_deck_section()`) → stores processed results in `st.session_state.processing_status['pitch_deck']`
2. **Analysis Section** (`analysis_section()`) → requires company directory to exist before proceeding

### Root Cause Identified

**The issue is a case sensitivity mismatch between stored company name and directory lookup:**

1. **During Pitch Deck Processing** (`src/processors/pitch_deck_processor.py:253`):
   - Company name extracted from metadata: `"ZINIOSA"` (uppercase)
   - `OutputManager.sanitize_company_name()` converts to lowercase: `"ziniosa"`
   - Directory created: `outputs/ziniosa/` (lowercase)
   - Session state stores original case: `st.session_state.company_name = "ZINIOSA"`

2. **During Analysis Section Check** (`src/ui/streamlit_app.py:123-126`):
   - `get_company_name_from_session()` returns: `"ZINIOSA"` (uppercase)
   - Directory lookup: `Path("outputs") / "ZINIOSA"` → `outputs/ZINIOSA/` (uppercase)
   - Directory check fails because actual directory is `outputs/ziniosa/` (lowercase)

### Key Files Affected

- `src/ui/streamlit_app.py:123-126` - Analysis section directory check
- `src/ui/streamlit_app.py:895-906` - `get_company_name_from_session()` function
- `src/utils/output_manager.py:34-58` - `sanitize_company_name()` method
- `src/processors/pitch_deck_processor.py:253` - Where company name is stored in session

### Evidence

- Metadata shows: `"startup_name": "ZINIOSA"` (uppercase)
- Directory exists: `outputs/ziniosa/` (lowercase)
- Session state stores: `"ZINIOSA"` (uppercase)
- Lookup fails because `outputs/ZINIOSA/` ≠ `outputs/ziniosa/`

## Solution Strategy

### Option 1: Consistent Sanitization (Recommended)

**Normalize company name consistently throughout the application:**

1. **Update session state storage** to store sanitized name:
   - In `pitch_deck_processor.py`, store `OutputManager.sanitize_company_name(company_name)` instead of raw name
   - Ensures session state matches actual directory name

2. **Update directory lookup** to use sanitized name:
   - In `get_company_name_from_session()`, return sanitized version
   - Ensures all directory lookups use correct case

**Pros:**
- Minimal code changes
- Maintains backward compatibility
- Follows existing sanitization pattern
- Most robust solution

**Cons:**
- UI displays lowercase company names

### Option 2: Store Both Names (Alternative)

**Store both original and sanitized names:**

1. **Extend session state** to store both:
   - `company_name_display`: Original case for UI display
   - `company_name_directory`: Sanitized for directory operations

2. **Update all directory operations** to use directory version
3. **Update UI display** to use display version

**Pros:**
- Preserves original casing for display
- Clear separation of concerns

**Cons:**
- More complex implementation
- Requires more extensive changes
- Risk of using wrong variable

### Option 3: Case-Insensitive Directory Lookup (Not Recommended)

**Use case-insensitive directory search:**

**Cons:**
- Platform-dependent behavior
- Performance overhead
- Doesn't address root cause

## Recommended Implementation Plan

**Phase 1: Fix Core Issue (Option 1)**
1. Update `pitch_deck_processor.py` to store sanitized company name in session
2. Update `get_company_name_from_session()` to ensure consistency
3. Test with existing ZINIOSA case

**Phase 2: Enhance Display (Optional)**
- If preserving display case is important, implement dual storage approach
- Update UI components to use display version
- Ensure all file operations use sanitized version

This approach ensures immediate fix while allowing future enhancement if needed.

## Implementation Status

✅ **COMPLETED - Option 1 (Consistent Sanitization) Implemented**

### Changes Made

1. **Updated `src/processors/pitch_deck_processor.py`**:
   - Modified company name extraction to store sanitized version in session state
   - Added logging to show sanitization process: `'ZINIOSA' → 'ziniosa'`
   - Ensures consistency between directory creation and session storage

2. **Updated `src/ui/streamlit_app.py`**:
   - Enhanced `get_company_name_from_session()` function
   - Always returns sanitized company name for directory operations
   - Handles both session state and processing results consistently

### Verification

- ✅ Sanitization function works correctly: `"ZINIOSA" → "ziniosa"`
- ✅ Directory lookup now works: `outputs/ziniosa` found
- ✅ Required files exist: `pitch_deck.md`, `metadata.json`
- ✅ Syntax check passed for both modified files

### Result

The "Company directory not found" error is now resolved. The analysis section will correctly find the `outputs/ziniosa/` directory when the company name "ZINIOSA" is processed, eliminating the case sensitivity mismatch.
