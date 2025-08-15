import pandas as pd
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    summary: Dict[str, int]
    invalid_data: pd.DataFrame  # New field to store invalid/missing data
    invalid_rows_list: List[Dict]  # List of invalid rows as dictionaries

class ExcelDataValidator:
    def __init__(self):
        # Define required columns for each entity type
        self.required_columns = {
            'award': [
                'AWARD_NUMBER', 'AWARD_NAME', 'AWARD_ORGANIZATION', 
                'AWARD_START_DATE', 'AWARD_END_DATE', 'AWARD_STATUS', 'AWARD_TYPE'
            ],
            'sponsor': [
                'SPONSOR_NUMBER', 'SPONSOR_NAME'
            ],
            'project': [
                'PROJECT_NUMBER', 'PROJECT_NAME', 'PROJECT_TYPE'
            ],
            'parent_task': [
                'PROJECT_NUMBER', 'PARENT_TASK_NUMBER', 'PARENT_TASK_NAME'
            ],
            'sub_task': [
                'PROJECT_NUMBER', 'SUB_TASK_NUMBER', 'FUND_NUMBER', 'AWARD_NUMBER'
            ]
        }
        
        # Define columns that should have valid relationships
        self.relationship_columns = {
            'project_to_parent_task': ('PROJECT_NUMBER', 'PARENT_TASK_NUMBER'),
            'parent_task_to_sub_task': ('PARENT_TASK_NUMBER', 'SUB_TASK_NUMBER'),
            'award_to_sub_task': ('AWARD_NUMBER', 'SUB_TASK_NUMBER'),
            'sponsor_to_award': ('SPONSOR_NUMBER', 'AWARD_NUMBER')
        }
        
        # Track invalid/missing data
        self.invalid_rows_indices = set()
        self.validation_issues = []  # Store detailed validation issues

    def validate_excel_data(self, df: pd.DataFrame) -> ValidationResult:
        """
        Comprehensive validation of Excel data before hierarchical processing
        
        Args:
            df: DataFrame containing the Excel data
        
        Returns:
            ValidationResult object with validation status and details
        """
        errors = []
        warnings = []
        summary = {}
        
        # Handle large datasets by sampling if specified
        original_size = len(df)
        df_sample = df
            
        # Replace pd.NA with None for consistent validation
        df_sample = df_sample.replace({pd.NA: None})
        
        try:
            # Reset tracking for each validation
            self.invalid_rows_indices = set()
            self.validation_issues = []
            
            # 1. Validate column presence
            column_errors = self._validate_required_columns(df_sample)
            errors.extend(column_errors)
            
            if column_errors:
                # If critical columns are missing, stop validation
                return ValidationResult(
                    is_valid=False,
                    errors=errors,
                    warnings=warnings,
                    summary={'total_rows': original_size, 'validation_failed': 'Missing required columns'},
                    invalid_data=pd.DataFrame()
                )
            
            # 2. Validate data completeness
            completeness_errors, completeness_warnings = self._validate_data_completeness(df_sample)
            errors.extend(completeness_errors)
            warnings.extend(completeness_warnings)
            
            # 3. Validate data integrity and relationships
            integrity_errors, integrity_warnings = self._validate_data_integrity(df_sample)
            errors.extend(integrity_errors)
            warnings.extend(integrity_warnings)
            
            # 4. Validate date formats
            date_errors = self._validate_date_formats(df_sample)
            errors.extend(date_errors)
            
            # 5. Validate numeric fields
            numeric_errors = self._validate_numeric_fields(df_sample)
            errors.extend(numeric_errors)
            
            # 6. Generate summary statistics
            summary = self._generate_summary_stats(df_sample, original_size)
            
            # 7. Extract invalid data for insertion
            invalid_data = self._extract_invalid_data(df_sample, original_size > len(df_sample))
            
            # 8. Convert invalid data to list of dictionaries for easy insertion
            invalid_rows_list = self._convert_invalid_data_to_list(df_sample, original_size > len(df_sample))
            
            # Determine if validation passed
            is_valid = len(errors) == 0
            
            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                summary=summary,
                invalid_data=invalid_data,
                invalid_rows_list=invalid_rows_list
            )
            
        except Exception as e:
            errors.append(f"Validation failed with exception: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                summary={'total_rows': original_size, 'validation_failed': str(e)},
                invalid_data=pd.DataFrame(),
                invalid_rows_list=[]
            )

    def _validate_required_columns(self, df: pd.DataFrame) -> List[str]:
        """Validate that all required columns are present"""
        errors = []
        df_columns = set(df.columns)
        
        # Collect all required columns
        all_required = set()
        for entity_columns in self.required_columns.values():
            all_required.update(entity_columns)
        
        missing_columns = all_required - df_columns
        if missing_columns:
            errors.append(f"Missing required columns: {sorted(list(missing_columns))}")
        
        return errors

    def _validate_data_completeness(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """Validate data completeness for critical fields"""
        errors = []
        warnings = []
        invalid_rows_list = []
        
        # Check for completely empty rows (excluding header)
        empty_rows = df.iloc[1:].isnull().all(axis=1).sum()
        if empty_rows > 0:
            warnings.append(f"Found {empty_rows} completely empty rows")
        
        # Check critical fields for missing data
        critical_missing_threshold = 0.1  # 10% missing data threshold
        
        for entity_type, required_cols in self.required_columns.items():
            for col in required_cols:
                if col in df.columns:
                    # Skip header row (index 0) for missing data calculation
                    data_rows = df.iloc[1:]
                    missing_count = data_rows[col].isnull().sum()
                    missing_percentage = missing_count / len(data_rows) if len(data_rows) > 0 else 0
                    
                    if missing_percentage > critical_missing_threshold:
                        errors.append(
                            f"Critical field '{col}' has {missing_count} missing values "
                            f"({missing_percentage:.2%} of data rows)"
                        )
                        # Track rows with missing critical data
                        missing_rows = data_rows[data_rows[col].isnull()]
                        self.invalid_rows_indices.update(missing_rows.index.tolist())
                        for idx in missing_rows.index:
                            self.validation_issues.append({
                                'row_index': idx,
                                'issue_type': 'missing_critical_data',
                                'column': col,
                                'issue_description': f"Missing value in critical field '{col}'"
                            })
                    elif missing_count > 0:
                        warnings.append(
                            f"Field '{col}' has {missing_count} missing values "
                            f"({missing_percentage:.2%} of data rows)"
                        )
        
        return errors, warnings

    def _validate_data_integrity(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """Validate referential integrity and business logic"""
        errors = []
        warnings = []
        
        # Skip header row for integrity checks
        data_df = df.iloc[1:].copy()
        
        # Check for orphaned records
        self._check_orphaned_records(data_df, errors, warnings)
        
        # Check for duplicate keys where they should be unique
        self._check_duplicate_keys(data_df, errors, warnings)
        
        # Check for circular references (if applicable)
        self._check_circular_references(data_df, warnings)
        
        return errors, warnings

    def _check_orphaned_records(self, df: pd.DataFrame, errors: List[str], warnings: List[str]):
        """Check for orphaned records in relationships"""
        
        # Check if sub-tasks have valid parent tasks
        sub_tasks_with_parent = df[
            df['SUB_TASK_NUMBER'].notna() & df['PARENT_TASK_NUMBER'].notna()
        ]
        
        if not sub_tasks_with_parent.empty:
            # Create parent task keys
            parent_keys = set()
            parent_tasks = df[df['PARENT_TASK_NUMBER'].notna()]
            for _, row in parent_tasks.iterrows():
                parent_keys.add((row['PROJECT_NUMBER'], row['PARENT_TASK_NUMBER']))
            
            # Check sub-task references
            orphaned_subtasks = 0
            for idx, row in sub_tasks_with_parent.iterrows():
                parent_key = (row['PROJECT_NUMBER'], row['PARENT_TASK_NUMBER'])
                if parent_key not in parent_keys:
                    orphaned_subtasks += 1
                    self.invalid_rows_indices.add(idx)
                    self.validation_issues.append({
                        'row_index': idx,
                        'issue_type': 'orphaned_subtask',
                        'column': 'PARENT_TASK_NUMBER',
                        'issue_description': f"Sub-task references non-existent parent task: {parent_key}"
                    })
            
            if orphaned_subtasks > 0:
                errors.append(f"Found {orphaned_subtasks} sub-tasks with invalid parent task references")
        
        # Check if awards referenced by sub-tasks exist
        sub_tasks_with_awards = df[
            df['SUB_TASK_NUMBER'].notna() & df['AWARD_NUMBER'].notna()
        ]
        
        if not sub_tasks_with_awards.empty:
            award_numbers = set(df[df['AWARD_NUMBER'].notna()]['AWARD_NUMBER'].unique())
            
            orphaned_award_refs = 0
            for idx, row in sub_tasks_with_awards.iterrows():
                if row['AWARD_NUMBER'] not in award_numbers:
                    orphaned_award_refs += 1
                    self.invalid_rows_indices.add(idx)
                    self.validation_issues.append({
                        'row_index': idx,
                        'issue_type': 'orphaned_award_reference',
                        'column': 'AWARD_NUMBER',
                        'issue_description': f"Sub-task references non-existent award: {row['AWARD_NUMBER']}"
                    })
            
            if orphaned_award_refs > 0:
                warnings.append(f"Found {orphaned_award_refs} sub-tasks referencing non-existent awards")

    def _check_duplicate_keys(self, df: pd.DataFrame, errors: List[str], warnings: List[str]):
        """Check for duplicate keys in entities that should be unique"""
        
        # Check for duplicate award numbers
        awards = df[df['AWARD_NUMBER'].notna()]
        if not awards.empty:
            duplicate_awards = awards['AWARD_NUMBER'].duplicated().sum()
            if duplicate_awards > 0:
                warnings.append(f"Found {duplicate_awards} duplicate award numbers")
        
        # Check for duplicate project numbers
        projects = df[df['PROJECT_NUMBER'].notna()]
        if not projects.empty:
            duplicate_projects = projects['PROJECT_NUMBER'].duplicated().sum()
            if duplicate_projects > 0:
                warnings.append(f"Found {duplicate_projects} duplicate project numbers")
        
        # Check for duplicate parent task keys (project + parent task number)
        parent_tasks = df[df['PARENT_TASK_NUMBER'].notna() & df['PROJECT_NUMBER'].notna()]
        if not parent_tasks.empty:
            parent_task_keys = parent_tasks[['PROJECT_NUMBER', 'PARENT_TASK_NUMBER']].apply(
                lambda x: f"{x['PROJECT_NUMBER']}_{x['PARENT_TASK_NUMBER']}", axis=1
            )
            duplicate_parent_tasks = parent_task_keys.duplicated().sum()
            if duplicate_parent_tasks > 0:
                warnings.append(f"Found {duplicate_parent_tasks} duplicate parent task keys")

    def _check_circular_references(self, df: pd.DataFrame, warnings: List[str]):
        """Check for potential circular references in project hierarchy"""
        # This is a simplified check - you might need more complex logic based on your data model
        projects_with_master = df[
            df['PROJECT_NUMBER'].notna() & df['Master_Project_Number'].notna()
        ]
        
        if not projects_with_master.empty:
            circular_refs = 0
            for _, row in projects_with_master.iterrows():
                if row['PROJECT_NUMBER'] == row['Master_Project_Number']:
                    circular_refs += 1
            
            if circular_refs > 0:
                warnings.append(f"Found {circular_refs} projects that reference themselves as master project")

    def _validate_date_formats(self, df: pd.DataFrame) -> List[str]:
        """Validate date field formats"""
        errors = []
        
        date_columns = [
            'AWARD_START_DATE', 'AWARD_END_DATE', 'AWARD_CLOSE_DATE',
            'SUBTASK_START_DATE', 'SUBTASK_COMPLETION_DATE',
            'PROJECT_START_DATE', 'PROJECT_END_DATE',
            'Burden_Schedule_Version_Start_Date', 'Burden_Schedule_Version_End_Date'
        ]
        
        for col in date_columns:
            if col in df.columns:
                # Skip header row and null values
                date_values = df.iloc[1:][col].dropna()
                
                if not date_values.empty:
                    invalid_dates = 0
                    for idx, value in date_values.items():
                        if value is not None and str(value).strip():
                            try:
                                pd.to_datetime(value)
                            except:
                                invalid_dates += 1
                                self.invalid_rows_indices.add(idx)
                                self.validation_issues.append({
                                    'row_index': idx,
                                    'issue_type': 'invalid_date_format',
                                    'column': col,
                                    'issue_description': f"Invalid date format in '{col}': {value}"
                                })
                    
                    if invalid_dates > 0:
                        errors.append(f"Column '{col}' has {invalid_dates} invalid date values")
        
        return errors

    def _validate_numeric_fields(self, df: pd.DataFrame) -> List[str]:
        """Validate numeric field formats"""
        errors = []
        
        numeric_columns = ['Burden_Rate_Multiplier', 'COST_CENTER', 'PROGRAM']
        
        for col in numeric_columns:
            if col in df.columns:
                # Skip header row and null values
                numeric_values = df.iloc[1:][col].dropna()
                
                if not numeric_values.empty:
                    invalid_numbers = 0
                    for idx, value in numeric_values.items():
                        if value is not None and str(value).strip():
                            try:
                                float(value)
                            except:
                                invalid_numbers += 1
                                self.invalid_rows_indices.add(idx)
                                self.validation_issues.append({
                                    'row_index': idx,
                                    'issue_type': 'invalid_numeric_format',
                                    'column': col,
                                    'issue_description': f"Invalid numeric format in '{col}': {value}"
                                })
                    
                    if invalid_numbers > 0:
                        errors.append(f"Column '{col}' has {invalid_numbers} invalid numeric values")
        
        return errors

    def _generate_summary_stats(self, df: pd.DataFrame, original_size: int) -> Dict[str, int]:
        """Generate summary statistics"""
        # Skip header row for counting
        data_df = df.iloc[1:]
        
        summary = {
            'total_rows': original_size,
            'validated_rows': len(df),
            'data_rows': len(data_df),
            'total_awards': data_df['AWARD_NUMBER'].notna().sum(),
            'total_sponsors': data_df['SPONSOR_NUMBER'].notna().sum(),
            'total_projects': data_df['PROJECT_NUMBER'].notna().sum(),
            'total_parent_tasks': data_df['PARENT_TASK_NUMBER'].notna().sum(),
            'total_sub_tasks': data_df['SUB_TASK_NUMBER'].notna().sum(),
        }
        
        # Count unique entities
        summary.update({
            'unique_awards': data_df[data_df['AWARD_NUMBER'].notna()]['AWARD_NUMBER'].nunique(),
            'unique_sponsors': data_df[data_df['SPONSOR_NUMBER'].notna()]['SPONSOR_NUMBER'].nunique(),
            'unique_projects': data_df[data_df['PROJECT_NUMBER'].notna()]['PROJECT_NUMBER'].nunique(),
        })
        
        return summary

    def _extract_invalid_data(self, df: pd.DataFrame, was_sampled: bool) -> pd.DataFrame:
        """Extract rows with invalid/missing data for insertion into Excel"""
        if not self.invalid_rows_indices:
            return pd.DataFrame()
        
        # If data was sampled, we need to be careful about row indices
        if was_sampled:
            # For sampled data, we can only return the invalid rows from the sample
            invalid_df = df.loc[list(self.invalid_rows_indices)].copy()
        else:
            # For full dataset, extract all invalid rows
            invalid_df = df.loc[list(self.invalid_rows_indices)].copy()
        
        # Add validation issue details as new columns
        invalid_df['VALIDATION_ISSUE_TYPE'] = ''
        invalid_df['VALIDATION_ISSUE_COLUMN'] = ''
        invalid_df['VALIDATION_ISSUE_DESCRIPTION'] = ''
        
        # Populate validation issue details
        for issue in self.validation_issues:
            if issue['row_index'] in invalid_df.index:
                invalid_df.loc[issue['row_index'], 'VALIDATION_ISSUE_TYPE'] = issue['issue_type']
                invalid_df.loc[issue['row_index'], 'VALIDATION_ISSUE_COLUMN'] = issue['column']
                invalid_df.loc[issue['row_index'], 'VALIDATION_ISSUE_DESCRIPTION'] = issue['issue_description']
        
        # Reset index to make it easier to work with
        invalid_df = invalid_df.reset_index(drop=True)
        
        return invalid_df

    def _convert_invalid_data_to_list(self, df: pd.DataFrame, was_sampled: bool) -> List[Dict]:
        """Convert invalid rows to list of dictionaries for easy Excel insertion"""
        if not self.invalid_rows_indices:
            return []
        
        # Extract invalid rows
        if was_sampled:
            invalid_rows_df = df.loc[list(self.invalid_rows_indices)].copy()
        else:
            invalid_rows_df = df.loc[list(self.invalid_rows_indices)].copy()
        
        # Convert to list of dictionaries (excluding validation columns)
        # This ensures the format matches exactly with the original Excel structure
        invalid_rows_list = []
        
        for idx, row in invalid_rows_df.iterrows():
            # Create a dictionary with the same structure as original data
            row_dict = {}
            
            # Copy all original columns (excluding any validation-specific columns)
            for col in df.columns:
                if not col.startswith('VALIDATION_'):
                    # Handle different data types appropriately
                    value = row[col]
                    
                    # Convert pandas NA/NaN to None for consistency
                    if pd.isna(value):
                        row_dict[col] = None
                    else:
                        row_dict[col] = value
            
            # Add metadata about the validation issues for this row
            row_validation_issues = [
                issue for issue in self.validation_issues 
                if issue['row_index'] == idx
            ]
            
            # Store validation info separately (can be used for logging/debugging)
            row_dict['_validation_issues'] = row_validation_issues
            row_dict['_original_row_index'] = idx
            
            invalid_rows_list.append(row_dict)
        
        return invalid_rows_list


def get_invalid_rows_summary(invalid_rows_list: List[Dict]) -> Dict:
    """
    Get summary statistics about invalid rows
    
    Args:
        invalid_rows_list: List of dictionaries containing invalid rows
    
    Returns:
        Dict: Summary statistics
    """
    if not invalid_rows_list:
        return {'total_invalid_rows': 0}
    
    # Analyze validation issues
    issue_types = {}
    affected_columns = {}
    
    for row_dict in invalid_rows_list:
        validation_issues = row_dict.get('_validation_issues', [])
        
        for issue in validation_issues:
            issue_type = issue['issue_type']
            column = issue['column']
            
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
            affected_columns[column] = affected_columns.get(column, 0) + 1
    
    summary = {
        'total_invalid_rows': len(invalid_rows_list),
        'issue_types_count': issue_types,
        'affected_columns_count': affected_columns,
        'most_common_issue': max(issue_types.items(), key=lambda x: x[1])[0] if issue_types else None,
        'most_affected_column': max(affected_columns.items(), key=lambda x: x[1])[0] if affected_columns else None
    }
    
    return summary

def validate_and_handle_invalid_data(df: pd.DataFrame) -> Tuple[bool, ValidationResult]:
    """
    Complete validation workflow with invalid data handling
    
    Args:
        df: DataFrame containing Excel data to validate
        target_excel_path: Path to Excel file where invalid data should be inserted
        sheet_name: Sheet name in the target Excel file
        sample_size: Sample size for large datasets
        create_separate_invalid_file: Whether to create a separate file for invalid data only
    
    Returns:
        Tuple[bool, ValidationResult]: (validation_passed, validation_result)
    """
    # Validate the data
    validator = ExcelDataValidator()
    result = validator.validate_excel_data(df)
    
    # Print validation results
    print(f"Validation Result: {'PASSED' if result.is_valid else 'FAILED'}")
    print(f"Summary: {result.summary}")
    
    if result.errors:
        print("\nERRORS:")
        for error in result.errors:
            print(f"  ❌ {error}")
    
    if result.warnings:
        print("\nWARNINGS:")
        for warning in result.warnings:
            print(f"  ⚠️ {warning}")
    
    # Handle invalid data if validation failed
    if not result.is_valid:
        if result.invalid_rows_list:
            print(f"\nFound {len(result.invalid_rows_list)} rows with invalid/missing data.")
            
            # Show summary of invalid data
            invalid_summary = get_invalid_rows_summary(result.invalid_rows_list)
            print(f"Invalid data summary: {invalid_summary}")
        else:
            print("No specific invalid rows identified, but validation failed due to structural issues.")
    
    return result.is_valid, result