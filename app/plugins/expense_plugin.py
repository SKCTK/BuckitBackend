import json
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from semantic_kernel.functions import kernel_function

from ..model import schemas
from ..controller import expenses_controller, financial_summary_controller
from ..database.session import get_db

class ExpensePlugin:
    """Plugin for managing expenses using Semantic Kernel."""

    #CREATING EXPENSES -------------------------------------------------------

    @kernel_function(
    description="""Create new expenses for a user's financial summary.
                        
    Expenses track the user's regular monthly spending in different categories.
    
    A financial summary must exist before expenses can be created.
    
    Ask for the following information one category at a time:
    1. Rent/mortgage amount
    2. Utilities amount
    3. Insurance amount
    4. Loan payments amount
    5. Groceries amount
    6. Transportation amount
    7. Subscriptions amount
    8. Entertainment amount
    
    Parse dollar amounts from natural language descriptions.
    Handle the conversation naturally - ask only one question at a time.
    """
    )
    async def create_expenses(
        self, 
        financial_summary_id: int,
        rent_mortgage: str = "0",
        utilities: str = "0",
        insurance: str = "0",
        loan_payments: str = "0",
        groceries: str = "0",
        transportation: str = "0",
        subscriptions: str = "0",
        entertainment: str = "0"
    ) -> str:
        """
        Create new expenses for a financial summary.
        """
        try:
            # Parse parameters
            rent_mortgage_float = float(rent_mortgage) if rent_mortgage else 0.0
            utilities_float = float(utilities) if utilities else 0.0
            insurance_float = float(insurance) if insurance else 0.0
            loan_payments_float = float(loan_payments) if loan_payments else 0.0
            groceries_float = float(groceries) if groceries else 0.0
            transportation_float = float(transportation) if transportation else 0.0
            subscriptions_float = float(subscriptions) if subscriptions else 0.0
            entertainment_float = float(entertainment) if entertainment else 0.0
            
            # Create expenses schema
            expenses_data = schemas.ExpensesCreate(
                financial_summary_id=financial_summary_id,
                rent_mortgage=rent_mortgage_float,
                utilities=utilities_float,
                insurance=insurance_float,
                loan_payments=loan_payments_float,
                groceries=groceries_float,
                transportation=transportation_float,
                subscriptions=subscriptions_float,
                entertainment=entertainment_float
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
            
            # Create expenses using controller
            try:
                new_expenses = expenses_controller.create_expenses(db, expenses_data)
                
                # Convert model to dictionary for JSON serialization
                expenses_dict = {
                    "id": new_expenses.id,
                    "financial_summary_id": new_expenses.financial_summary_id,
                    "rent_mortgage": new_expenses.rent_mortgage,
                    "utilities": new_expenses.utilities,
                    "insurance": new_expenses.insurance,
                    "loan_payments": new_expenses.loan_payments,
                    "groceries": new_expenses.groceries,
                    "transportation": new_expenses.transportation,
                    "subscriptions": new_expenses.subscriptions,
                    "entertainment": new_expenses.entertainment
                }
                
                return json.dumps({
                    "success": True,
                    "message": "Expenses created successfully",
                    "data": expenses_dict
                })
                
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to create expenses: {str(e)}"
            })

    #UPDATING EXPENSES -------------------------------------------------------

    @kernel_function(
        description="""Update a user's expenses.
        
        User can update any of the following expense categories:
        - rent_mortgage
        - utilities
        - insurance
        - loan_payments
        - groceries
        - transportation
        - subscriptions
        - entertainment
        
        Ask which categories they want to change.
        Only ask about the specific categories they want to modify.
        
        Handle the conversation in a natural way - don't try to collect all categories at once.
        Parse dollar amounts from natural language descriptions.
        """
    )
    async def update_expenses(
        self,
        expenses_id: int,
        rent_mortgage: Optional[str] = None,
        utilities: Optional[str] = None,
        insurance: Optional[str] = None,
        loan_payments: Optional[str] = None,
        groceries: Optional[str] = None,
        transportation: Optional[str] = None,
        subscriptions: Optional[str] = None,
        entertainment: Optional[str] = None
    ) -> str:
        """
        Update existing expenses.
        """
        try:
            # Parse parameters that were provided
            update_data = {}
            
            if rent_mortgage is not None:
                update_data["rent_mortgage"] = float(rent_mortgage)
                
            if utilities is not None:
                update_data["utilities"] = float(utilities)
                
            if insurance is not None:
                update_data["insurance"] = float(insurance)
                
            if loan_payments is not None:
                update_data["loan_payments"] = float(loan_payments)
                
            if groceries is not None:
                update_data["groceries"] = float(groceries)
                
            if transportation is not None:
                update_data["transportation"] = float(transportation)
                
            if subscriptions is not None:
                update_data["subscriptions"] = float(subscriptions)
                
            if entertainment is not None:
                update_data["entertainment"] = float(entertainment)
            
            # Create update schema
            expenses_update = schemas.ExpensesUpdate(**update_data)
            
            # Get database session
            db = next(get_db())
            
            # Update expenses using controller
            try:
                updated_expenses = expenses_controller.update_expenses(db, expenses_id, expenses_update)
                
                if not updated_expenses:
                    return json.dumps({
                        "success": False,
                        "error": f"Expenses with ID {expenses_id} not found"
                    })
                
                # Convert model to dictionary for JSON serialization
                expenses_dict = {
                    "id": updated_expenses.id,
                    "financial_summary_id": updated_expenses.financial_summary_id,
                    "rent_mortgage": updated_expenses.rent_mortgage,
                    "utilities": updated_expenses.utilities,
                    "insurance": updated_expenses.insurance,
                    "loan_payments": updated_expenses.loan_payments,
                    "groceries": updated_expenses.groceries,
                    "transportation": updated_expenses.transportation,
                    "subscriptions": updated_expenses.subscriptions,
                    "entertainment": updated_expenses.entertainment
                }
                
                return json.dumps({
                    "success": True,
                    "message": "Expenses updated successfully",
                    "data": expenses_dict
                })
                
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to update expenses: {str(e)}"
            })

    #DELETING EXPENSES -------------------------------------------------------

    @kernel_function(
        description="""Delete a user's expenses.
        
        Confirm if they want to delete the expenses.
        """
    )
    async def delete_expenses(
        self,
        expenses_id: int
    ) -> str:
        """
        Delete expenses.
        """
        try:
            # Get database session
            db = next(get_db())       
            
            # Delete expenses using controller
            try:
                deleted_expenses = expenses_controller.delete_expenses(db, expenses_id)
                
                if not deleted_expenses:
                    return json.dumps({
                        "success": False,
                        "error": f"Expenses with ID {expenses_id} not found"
                    })
                    
                return json.dumps({
                    "success": True,
                    "message": "Expenses deleted successfully"
                })
                
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to delete expenses: {str(e)}"
            })
            
    #GETTING EXPENSES -------------------------------------------------------

    @kernel_function(
        description="""Get a user's expenses.
        
        Retrieves the expenses data for a user.
        """
    )
    async def get_expenses(
        self,
        financial_summary_id: int
    ) -> str:
        """
        Get expenses by financial summary ID.
        """
        try:
            # Get database session
            db = next(get_db())       
            
            # Get expenses using controller
            try:
                expenses = expenses_controller.get_expenses_by_financial_summary(db, financial_summary_id)
                
                if not expenses:
                    return json.dumps({
                        "success": False,
                        "error": f"Expenses for financial summary ID {financial_summary_id} not found"
                    })
                
                # Convert model to dictionary for JSON serialization
                expenses_dict = {
                    "id": expenses.id,
                    "financial_summary_id": expenses.financial_summary_id,
                    "rent_mortgage": expenses.rent_mortgage,
                    "utilities": expenses.utilities,
                    "insurance": expenses.insurance,
                    "loan_payments": expenses.loan_payments,
                    "groceries": expenses.groceries,
                    "transportation": expenses.transportation,
                    "subscriptions": expenses.subscriptions,
                    "entertainment": expenses.entertainment
                }
                
                return json.dumps({
                    "success": True,
                    "data": expenses_dict
                })
                
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to retrieve expenses: {str(e)}"
            })