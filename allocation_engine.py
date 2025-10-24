"""
BTP/MTP Allocation Engine
Implements the allocation algorithm based on CGPA sorting and preference cycling
"""

import pandas as pd
import logging
from typing import Dict, List, Tuple
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('allocation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AllocationEngine:
    """Main class for handling BTP/MTP allocation"""
    
    def __init__(self):
        self.faculties = []
        self.students_data = None
        self.allocation_results = None
        self.preference_stats = None
        
    def load_data(self, file_path: str) -> bool:
        """
        Load student data from CSV file
        
        Args:
            file_path: Path to the input CSV file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Loading data from {file_path}")
            self.students_data = pd.read_csv(file_path)
            
            # Extract faculty names (columns after CGPA)
            cgpa_col_index = self.students_data.columns.get_loc('CGPA')
            self.faculties = list(self.students_data.columns[cgpa_col_index + 1:])
            
            logger.info(f"Loaded {len(self.students_data)} students")
            logger.info(f"Found {len(self.faculties)} faculties: {self.faculties}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return False
    
    def sort_students_by_cgpa(self) -> pd.DataFrame:
        """
        Sort students by CGPA in descending order
        
        Returns:
            pd.DataFrame: Sorted student data
        """
        try:
            logger.info("Sorting students by CGPA (descending)")
            sorted_data = self.students_data.sort_values('CGPA', ascending=False).reset_index(drop=True)
            logger.info(f"Sorted {len(sorted_data)} students by CGPA")
            return sorted_data
            
        except Exception as e:
            logger.error(f"Error sorting students: {str(e)}")
            raise
    
    def allocate_students(self) -> pd.DataFrame:
        """
        Allocate students to faculties using mod n algorithm with preference cycling
        
        Returns:
            pd.DataFrame: Allocation results
        """
        try:
            logger.info("Starting student allocation process")
            
            # Sort students by CGPA
            sorted_students = self.sort_students_by_cgpa()
            n_faculties = len(self.faculties)
            
            # Initialize allocation results
            allocation_results = []
            
            # Track faculty capacity (each faculty gets exactly one student per cycle)
            faculty_cycle_count = {faculty: 0 for faculty in self.faculties}
            
            for idx, student in sorted_students.iterrows():
                student_allocated = False
                preference_rank = 1
                
                # Try each preference in order
                while preference_rank <= len(self.faculties) and not student_allocated:
                    # Find faculty at this preference rank
                    faculty_at_rank = None
                    for faculty in self.faculties:
                        if student[faculty] == preference_rank:
                            faculty_at_rank = faculty
                            break
                    
                    if faculty_at_rank:
                        # Check if this faculty can take a student in current cycle
                        current_cycle = idx // n_faculties
                        faculty_cycle = faculty_cycle_count[faculty_at_rank]
                        
                        if faculty_cycle == current_cycle:
                            # Allocate student to this faculty
                            allocation_results.append({
                                'Roll': student['Roll'],
                                'Name': student['Name'],
                                'Email': student['Email'],
                                'CGPA': student['CGPA'],
                                'Allocated': faculty_at_rank,
                                'Preference_Rank': preference_rank
                            })
                            
                            faculty_cycle_count[faculty_at_rank] += 1
                            student_allocated = True
                            logger.debug(f"Allocated {student['Roll']} to {faculty_at_rank} (preference {preference_rank})")
                    
                    preference_rank += 1
                
                # If no allocation found, assign to first available faculty
                if not student_allocated:
                    # Find faculty with minimum cycle count
                    min_cycle_faculty = min(faculty_cycle_count.keys(), 
                                          key=lambda x: faculty_cycle_count[x])
                    
                    allocation_results.append({
                        'Roll': student['Roll'],
                        'Name': student['Name'],
                        'Email': student['Email'],
                        'CGPA': student['CGPA'],
                        'Allocated': min_cycle_faculty,
                        'Preference_Rank': 'Unallocated'
                    })
                    
                    faculty_cycle_count[min_cycle_faculty] += 1
                    logger.warning(f"Unallocated student {student['Roll']} assigned to {min_cycle_faculty}")
            
            self.allocation_results = pd.DataFrame(allocation_results)
            logger.info(f"Allocation completed for {len(allocation_results)} students")
            
            return self.allocation_results
            
        except Exception as e:
            logger.error(f"Error in allocation process: {str(e)}")
            raise
    
    def generate_preference_stats(self) -> pd.DataFrame:
        """
        Generate faculty preference statistics
        
        Returns:
            pd.DataFrame: Preference statistics
        """
        try:
            logger.info("Generating preference statistics")
            
            if self.students_data is None:
                raise ValueError("No student data loaded")
            
            # Initialize stats dataframe
            max_preferences = len(self.faculties)
            stats_data = []
            
            for faculty in self.faculties:
                faculty_stats = {'Fac': faculty}
                
                # Count students for each preference rank
                for pref_rank in range(1, max_preferences + 1):
                    count = (self.students_data[faculty] == pref_rank).sum()
                    faculty_stats[f'Count Pref {pref_rank}'] = count
                
                stats_data.append(faculty_stats)
            
            self.preference_stats = pd.DataFrame(stats_data)
            logger.info("Preference statistics generated successfully")
            
            return self.preference_stats
            
        except Exception as e:
            logger.error(f"Error generating preference stats: {str(e)}")
            raise
    
    def save_allocation_results(self, output_path: str) -> bool:
        """
        Save allocation results to CSV
        
        Args:
            output_path: Path to save the results
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.allocation_results is None:
                raise ValueError("No allocation results to save")
            
            # Prepare output data (remove preference rank column for final output)
            output_data = self.allocation_results[['Roll', 'Name', 'Email', 'CGPA', 'Allocated']].copy()
            
            output_data.to_csv(output_path, index=False)
            logger.info(f"Allocation results saved to {output_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving allocation results: {str(e)}")
            return False
    
    def save_preference_stats(self, output_path: str) -> bool:
        """
        Save preference statistics to CSV
        
        Args:
            output_path: Path to save the statistics
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.preference_stats is None:
                raise ValueError("No preference statistics to save")
            
            self.preference_stats.to_csv(output_path, index=False)
            logger.info(f"Preference statistics saved to {output_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving preference statistics: {str(e)}")
            return False
    
    def get_allocation_summary(self) -> Dict:
        """
        Get summary of allocation results
        
        Returns:
            Dict: Summary statistics
        """
        try:
            if self.allocation_results is None:
                return {}
            
            summary = {
                'total_students': len(self.allocation_results),
                'faculty_distribution': self.allocation_results['Allocated'].value_counts().to_dict(),
                'preference_satisfaction': {
                    'pref_1': (self.allocation_results['Preference_Rank'] == 1).sum(),
                    'pref_2': (self.allocation_results['Preference_Rank'] == 2).sum(),
                    'pref_3': (self.allocation_results['Preference_Rank'] == 3).sum(),
                    'other': (self.allocation_results['Preference_Rank'] > 3).sum()
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {}


def main():
    """Main function for testing the allocation engine"""
    try:
        # Initialize allocation engine
        engine = AllocationEngine()
        
        # Load data
        if not engine.load_data('input_btp_mtp_allocation.csv'):
            logger.error("Failed to load data")
            return
        
        # Perform allocation
        allocation_results = engine.allocate_students()
        
        # Generate preference statistics
        preference_stats = engine.generate_preference_stats()
        
        # Save results
        engine.save_allocation_results('output_allocation.csv')
        engine.save_preference_stats('output_preference_stats.csv')
        
        # Print summary
        summary = engine.get_allocation_summary()
        logger.info(f"Allocation Summary: {summary}")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")


if __name__ == "__main__":
    main()
