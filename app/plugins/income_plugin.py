import json
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from semantic_kernel.functions import kernel_function

from ..model import schemas
from ..controller import income_controller, financial_summary_controller
from ..database.session import get_db

class IncomePlugin:
    """Plugin for managing income using Semantic Kernel."""

    #CREATING INCOME -------------------------------------------------------

    @kernel_function(
    description="""Create new income for a user's financial summary.
                        
    Income tracks the user's regular monthly income from different sources.
    
    A financial summary must exist before income can be created.
    
    Ask for the following information one at a time:
    1. Salary amount
    2. Investments income amount
    3. Business income amount
    
    Parse dollar amounts from natural language descriptions.
    Handle the conversation naturally - ask only one question at a time.
    """
    )
    async def create_income(
        self, 
        financial_summary_id: int,
        salary: str = "0",
        investments: str = "0",
        business_income: str = "0"
    ) -> str:
        """
        Create new income for a financial summary.
        """
        try:
            # Parse parameters
            salary_float = float(salary) if salary else 0.0
            investments_float = float(investments) if investments else 0.0
            business_income_float = float(business_income) if business_income else 0.0
            
            # Create income schema
            income_data = schemas.IncomeCreate(
                financial_summary_id=financial_summary_id,
                salary=salary_float,
                investments=investments_float,
                business_income=business_income_float
            )
            
            # Get database session
            db = next(get_db())
            
            # First check if financial summary exists
            summary = financial_summary_controller.get_financial_summary(db, financial_summary_id)
            if not summary:
                return json.dumps({
                    "success": False,
                    "error": f"Financial summary with ID {financial_summary_id} not found"
                })
            
            # Create income using controller
            try:
                new_income = income_controller.create_income(db, income_data)
                
                # Convert model to dictionary for JSON serialization
                income_dict = {
                    "id": new_income.id,
                    "financial_summary_id": new_income.financial_summary_id,
                    "salary": new_income.salary,
                    "investments": new_income.investments,
                    "business_income": new_income.business_income
                }
                
                return json.dumps({
                    "success": True,
                    "message": "Income created successfully",
                    "data": income_dict
                })
                
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to create income: {str(e)}"
            })

    #UPDATING INCOME -------------------------------------------------------

    @kernel_function(
        description="""Update a user's income.
        
        User can update any of the following income sources:
        - salary
        - investments
        - business_income
        
        Ask which sources they want to change.
        Only ask about the specific sources they want to modify.
        
        Handle the conversation in a natural way - don't try to collect all sources at once.
        Parse dollar amounts from natural language descriptions.
        """
    )
    async def update_income(
        self,
        income_id: int,
        salary: Optional[str] = None,
        investments: Optional[str] = None,
        business_income: Optional[str] = None
    ) -> str:
        """
        Update existing income.
        """
        try:
            # Parse parameters that were provided
            update_data = {}
            
            if salary is not None:
                update_data["salary"] = float(salary)
                
            if investments is not None:
                update_data["investments"] = float(investments)
                
            if business_income is not None:
                update_data["business_income"] = float(business_income)
            
            # Create update schema
            income_update = schemas.IncomeUpdate(**update_data)
            
            # Get database session
            db = next(get_db())
            
            # Update income using controller
            try:
                updated_income = income_controller.update_income(db, income_id, income_update)
                
                if not updated_income:
                    return json.dumps({
                        "success": False,
                        "error": f"Income with ID {income_id} not found"
                    })
                
                # Convert model to dictionary for JSON serialization
                income_dict = {
                    "id": updated_income.id,
                    "financial_summary_id": updated_income.financial_summary_id,
                    "salary": updated_income.salary,
                    "investments": updated_income.investments,
                    "business_income": updated_income.business_income
                }
                
                return json.dumps({
                    "success": True,
                    "message": "Income updated successfully",
                    "data": income_dict
                })
                
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to update income: {str(e)}"
            })

    #DELETING INCOME -------------------------------------------------------

    @kernel_function(
        description="""Delete a user's income.
        
        Confirm if they want to delete the income.
        """
    )
    async def delete_income(
        self,
        income_id: int
    ) -> str:
        """
        Delete income.
        """
        try:
            # Get database session
            db = next(get_db())       
            
            # Delete income using controller
            try:
                deleted_income = income_controller.delete_income(db, income_id)
                
                if not deleted_income:
                    return json.dumps({
                        "success": False,
                        "error": f"Income with ID {income_id} not found"
                    })
                    
                return json.dumps({
                    "success": True,
                    "message": "Income deleted successfully"
                })
                
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to delete income: {str(e)}"
            })
            
    #GETTING INCOME -------------------------------------------------------

    @kernel_function(
        description="""Get a user's income.
        
        Retrieves the income data for a user.
        """
    )
    async def get_income(
        self,
        financial_summary_id: int
    ) -> str:
        """
        Get income by financial summary ID.
        """
        try:
            # Get database session
            db = next(get_db())       
            
            # Get income using controller
            try:
                income = income_controller.get_income_by_financial_summary(db, financial_summary_id)
                
                if not income:
                    return json.dumps({
                        "success": False,
                        "error": f"Income for financial summary ID {financial_summary_id} not found"
                    })
                
                # Convert model to dictionary for JSON serialization
                income_dict = {
                    "id": income.id,
                    "financial_summary_id": income.financial_summary_id,
                    "salary": income.salary,
                    "investments": income.investments,
                    "business_income": income.business_income
                }
                
                return json.dumps({
                    "success": True,
                    "data": income_dict
                })
                
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to retrieve income: {str(e)}"
            })