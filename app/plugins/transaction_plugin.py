import json
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from semantic_kernel.functions import kernel_function

from ..model import schemas
from ..controller import transaction_controller
from ..database.session import get_db

class TransactionPlugin:
    """Plugin for managing transactions using Semantic Kernel."""

    #CREATING TRANSACTION -------------------------------------------------------

    @kernel_function(
    description="""Create a new transaction for a user.
                        
    Transactions record financial activities like spending or income.
    
    Ask for the following information one at a time:
    1. Amount (positive for income, negative for expenses)
    2. Description of the transaction
    3. Category (e.g., Food, Housing, Transportation, Income)
    4. Reference number (optional)
    5. Additional notes (optional)
    
    Parse dollar amounts from natural language descriptions.
    Handle the conversation naturally - ask only one question at a time.
    """
    )
    async def create_transaction(
        self, 
        user_id: str,
        amount: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        transaction_date: Optional[str] = None,
        reference: Optional[str] = None,
        notes: Optional[str] = None,
        is_reconciled: str = "false"
    ) -> str:
        """
        Create a new transaction for a user.
        """
        try:
            # Parse parameters
            user_id_int = int(user_id)
            amount_float = float(amount)
            is_reconciled_bool = is_reconciled.lower() == "true"
            
            # Create transaction schema
            transaction_data = schemas.TransactionCreate(
                user_id=user_id_int,
                amount=amount_float,
                description=description,
                category=category,
                transaction_date=transaction_date or datetime.now(),
                reference=reference,
                notes=notes,
                is_reconciled=is_reconciled_bool
            )
            
            # Get database session
            db = next(get_db())
            
            # Create transaction using controller
            try:
                new_transaction = transaction_controller.create_transaction(db, transaction_data)
                
                # Convert model to dictionary for JSON serialization
                transaction_dict = {
                    "id": new_transaction.id,
                    "user_id": new_transaction.user_id,
                    "amount": new_transaction.amount,
                    "description": new_transaction.description,
                    "category": new_transaction.category,
                    "transaction_date": new_transaction.transaction_date.isoformat() if new_transaction.transaction_date else None,
                    "reference": new_transaction.reference,
                    "notes": new_transaction.notes,
                    "is_reconciled": new_transaction.is_reconciled
                }
                
                return json.dumps({
                    "success": True,
                    "message": "Transaction created successfully",
                    "data": transaction_dict
                })
                
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to create transaction: {str(e)}"
            })

    #UPDATING TRANSACTION -------------------------------------------------------

    @kernel_function(
        description="""Update a transaction.
        
        User can update any of the following transaction properties:
        - amount
        - description
        - category
        - transaction_date
        - reference
        - notes
        - is_reconciled (true/false)
        
        Ask which properties they want to change.
        Only ask about the specific properties they want to modify.
        
        Handle the conversation in a natural way - don't try to collect all properties at once.
        Parse dollar amounts and dates from natural language descriptions.
        """
    )
    async def update_transaction(
        self,
        transaction_id: int,
        amount: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        transaction_date: Optional[str] = None,
        reference: Optional[str] = None,
        notes: Optional[str] = None,
        is_reconciled: Optional[str] = None
    ) -> str:
        """
        Update an existing transaction.
        """
        try:
            # Parse parameters that were provided
            update_data = {}
            
            if amount is not None:
                update_data["amount"] = float(amount)
                
            if description is not None:
                update_data["description"] = description
                
            if category is not None:
                update_data["category"] = category
                
            if transaction_date is not None:
                update_data["transaction_date"] = transaction_date
                
            if reference is not None:
                update_data["reference"] = reference
                
            if notes is not None:
                update_data["notes"] = notes
                
            if is_reconciled is not None:
                update_data["is_reconciled"] = is_reconciled.lower() == "true"
            
            # Create update schema
            transaction_update = schemas.TransactionUpdate(**update_data)
            
            # Get database session
            db = next(get_db())
            
            # Update transaction using controller
            try:
                updated_transaction = transaction_controller.update_transaction(db, transaction_id, transaction_update)
                
                if not updated_transaction:
                    return json.dumps({
                        "success": False,
                        "error": f"Transaction with ID {transaction_id} not found"
                    })
                
                # Convert model to dictionary for JSON serialization
                transaction_dict = {
                    "id": updated_transaction.id,
                    "user_id": updated_transaction.user_id,
                    "amount": updated_transaction.amount,
                    "description": updated_transaction.description,
                    "category": updated_transaction.category,
                    "transaction_date": updated_transaction.transaction_date.isoformat() if updated_transaction.transaction_date else None,
                    "reference": updated_transaction.reference,
                    "notes": updated_transaction.notes,
                    "is_reconciled": updated_transaction.is_reconciled
                }
                
                return json.dumps({
                    "success": True,
                    "message": "Transaction updated successfully",
                    "data": transaction_dict
                })
                
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to update transaction: {str(e)}"
            })

    #DELETING TRANSACTION -------------------------------------------------------

    @kernel_function(
        description="""Delete a transaction.
        
        Confirm if the user wants to delete the transaction.
        """
    )
    async def delete_transaction(
        self,
        transaction_id: int
    ) -> str:
        """
        Delete a transaction.
        """
        try:
            # Get database session
            db = next(get_db())       
            
            # Delete transaction using controller
            try:
                deleted_transaction = transaction_controller.delete_transaction(db, transaction_id)
                
                if not deleted_transaction:
                    return json.dumps({
                        "success": False,
                        "error": f"Transaction with ID {transaction_id} not found"
                    })
                    
                return json.dumps({
                    "success": True,
                    "message": "Transaction deleted successfully"
                })
                
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to delete transaction: {str(e)}"
            })
            
    #GETTING TRANSACTIONS -------------------------------------------------------

    @kernel_function(
        description="""Get a user's transactions.
        
        Retrieves the transactions for a user, optionally filtered by category.
        """
    )
    async def get_transactions(
        self,
        user_id: int,
        category: Optional[str] = None
    ) -> str:
        """
        Get transactions by user ID.
        """
        try:
            # Get database session
            db = next(get_db())       
            
            # Get transactions using controller
            try:
                transactions = transaction_controller.get_user_transactions(db, user_id)
                
                if not transactions:
                    return json.dumps({
                        "success": False,
                        "error": f"No transactions found for user ID {user_id}"
                    })
                
                # Filter by category if provided
                if category:
                    transactions = [t for t in transactions if t.category == category]
                
                # Convert models to dictionaries for JSON serialization
                transactions_list = []
                for transaction in transactions:
                    transactions_list.append({
                        "id": transaction.id,
                        "user_id": transaction.user_id,
                        "amount": transaction.amount,
                        "description": transaction.description,
                        "category": transaction.category,
                        "transaction_date": transaction.transaction_date.isoformat() if transaction.transaction_date else None,
                        "reference": transaction.reference,
                        "notes": transaction.notes,
                        "is_reconciled": transaction.is_reconciled
                    })
                
                return json.dumps({
                    "success": True,
                    "data": transactions_list
                })
                
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to retrieve transactions: {str(e)}"
            })