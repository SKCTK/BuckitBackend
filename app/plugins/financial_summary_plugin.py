import json
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from semantic_kernel.functions import kernel_function

from ..model import schemas
from ..controller import financial_summary_controller
from ..database.session import get_db

class FinancialSummaryPlugin:
    """Plugin for managing financial summaries using Semantic Kernel."""

    #CREATING FINANCIAL SUMMARY -------------------------------------------------------

    @kernel_function(
    description="""Create a new financial summary for a user.
                        
    A financial summary contains the user's overall financial picture.
    This must be created before adding expenses or income.

    Ask for the following information one at a time:
    1. Savings balance (how much the user has in savings accounts)
    2. Investment balance (how much the user has in investment accounts)
    3. Debt balance (how much debt the user has)
    
    Parse dollar amounts from natural language descriptions.
    Handle the conversation naturally - ask only one question at a time.
    """
    )
    async def create_financial_summary(
        self, 
        user_id: str,
        savings_balance: str = "0",
        investment_balance: str = "0",
        debt_balance: str = "0"
    ) -> str:
        """
        Create a new financial summary for a user.
        """
        try:
            # Parse parameters
            user_id_int = int(user_id)
            savings_balance_float = float(savings_balance) if savings_balance else 0.0
            investment_balance_float = float(investment_balance) if investment_balance else 0.0
            debt_balance_float = float(debt_balance) if debt_balance else 0.0
            
            # Create financial summary schema
            summary_data = schemas.FinancialSummaryCreate(
                user_id=user_id_int,
                savings_balance=savings_balance_float,
                investment_balance=investment_balance_float,
                debt_balance=debt_balance_float
            )
            
            # Get database session
            db = next(get_db())
            
            # Create financial summary using controller
            try:
                new_summary = financial_summary_controller.create_financial_summary(db, summary_data)
                
                # Convert model to dictionary for JSON serialization
                summary_dict = {
                    "id": new_summary.id,
                    "user_id": new_summary.user_id,
                    "savings_balance": new_summary.savings_balance,
                    "investment_balance": new_summary.investment_balance,
                    "debt_balance": new_summary.debt_balance
                }
                
                return json.dumps({
                    "success": True,
                    "message": "Financial summary created successfully",
                    "data": summary_dict
                })
                
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to create financial summary: {str(e)}"
            })

    #UPDATING FINANCIAL SUMMARY -------------------------------------------------------

    @kernel_function(
        description="""Update a user's financial summary.
        
        User can update any of the following financial summary properties:
        - savings_balance
        - investment_balance
        - debt_balance
        
        Ask which properties they want to change.
        Only ask about the specific properties they want to modify.
        
        Handle the conversation in a natural way - don't try to collect all properties at once.
        Parse dollar amounts from natural language descriptions.
        """
    )
    async def update_financial_summary(
        self,
        financial_summary_id: int,
        savings_balance: Optional[str] = None,
        investment_balance: Optional[str] = None,
        debt_balance: Optional[str] = None
    ) -> str:
        """
        Update an existing financial summary.
        """
        try:
            # Parse parameters that were provided
            update_data = {}
            
            if savings_balance is not None:
                update_data["savings_balance"] = float(savings_balance)
                
            if investment_balance is not None:
                update_data["investment_balance"] = float(investment_balance)
                
            if debt_balance is not None:
                update_data["debt_balance"] = float(debt_balance)
            
            # Create update schema
            summary_update = schemas.FinancialSummaryUpdate(**update_data)
            
            # Get database session
            db = next(get_db())
            
            # Update financial summary using controller
            try:
                updated_summary = financial_summary_controller.update_financial_summary(db, financial_summary_id, summary_update)
                
                if not updated_summary:
                    return json.dumps({
                        "success": False,
                        "error": f"Financial summary with ID {financial_summary_id} not found"
                    })
                
                # Convert model to dictionary for JSON serialization
                summary_dict = {
                    "id": updated_summary.id,
                    "user_id": updated_summary.user_id,
                    "savings_balance": updated_summary.savings_balance,
                    "investment_balance": updated_summary.investment_balance,
                    "debt_balance": updated_summary.debt_balance
                }
                
                return json.dumps({
                    "success": True,
                    "message": "Financial summary updated successfully",
                    "data": summary_dict
                })
                
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to update financial summary: {str(e)}"
            })

    #DELETING FINANCIAL SUMMARY -------------------------------------------------------

    @kernel_function(
        description="""Delete a financial summary.
        
        Warn the user that deleting a financial summary will also delete associated expenses and income.
        
        Confirm if they want to delete the financial summary.
        """
    )
    async def delete_financial_summary(
        self,
        financial_summary_id: int
    ) -> str:
        """
        Delete a financial summary.
        """
        try:
            # Get database session
            db = next(get_db())       
            
            # Delete financial summary using controller
            try:
                deleted_summary = financial_summary_controller.delete_financial_summary(db, financial_summary_id)
                
                if not deleted_summary:
                    return json.dumps({
                        "success": False,
                        "error": f"Financial summary with ID {financial_summary_id} not found"
                    })
                    
                return json.dumps({
                    "success": True,
                    "message": "Financial summary deleted successfully"
                })
                
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to delete financial summary: {str(e)}"
            })

    #GETTING FINANCIAL SUMMARY -------------------------------------------------------

    @kernel_function(
        description="""Get a user's financial summary.
        
        Retrieves the financial summary data for a user.
        """
    )
    async def get_financial_summary(
        self,
        user_id: int
    ) -> str:
        """
        Get a financial summary by user ID.
        """
        try:
            # Get database session
            db = next(get_db())       
            
            # Get financial summary using controller
            try:
                summary = financial_summary_controller.get_financial_summary_by_user(db, user_id)
                
                if not summary:
                    return json.dumps({
                        "success": False,
                        "error": f"Financial summary for user ID {user_id} not found"
                    })
                
                # Convert model to dictionary for JSON serialization
                summary_dict = {
                    "id": summary.id,
                    "user_id": summary.user_id,
                    "savings_balance": summary.savings_balance,
                    "investment_balance": summary.investment_balance,
                    "debt_balance": summary.debt_balance
                }
                
                return json.dumps({
                    "success": True,
                    "data": summary_dict
                })
                
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to retrieve financial summary: {str(e)}"
            })