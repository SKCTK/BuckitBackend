import json
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from semantic_kernel.functions import kernel_function

from ..model import schemas
from ..controller import bucket_controller
from ..database.session import get_db

class BucketPlugin:
    """Plugin for managing budget buckets using Semantic Kernel."""

#CREATING BUCKET -------------------------------------------------------

    @kernel_function(
    description="""Create a new budget bucket for a user.
                        
    Buckets help users allocate savings toward specific financial goals.

    This is a step-by-step process. Ask EXACTLY ONE question at a time.
    NEVER present a numbered list of all required information.
    NEVER mention upcoming questions before they're reached.
    NEVER ask about status - all buckets are 'active' by default.
    Accept natural language date descriptions without requiring a specific format.

    Ask questions in this exact sequence:
    1. Name of bucket
    2. Target amount
    3. Current saved amount
    4. Priority (1-10)
    5. Deadline (parse user answer into YYYY-MM-DD format.)

    Each question must be in its own separate response.
    
    
    """
    )
    async def create_bucket(
        self, 
        user_id: str,
        name: str,
        target_amount: str = "0",
        current_saved_amount: str = "0",
        priority_score: str = "1",
        deadline: Optional[str] = None,
        status: str = "active"
    ) -> str:
        """
        Create a new budget bucket for a user.
        """
        try:
            # Parse parameters
            user_id_int = int(user_id)
            target_amount_float = float(target_amount) if target_amount else 0.0
            current_saved_amount_float = float(current_saved_amount) if current_saved_amount else 0.0
            priority_score_int = int(priority_score) if priority_score else 1
            
            # Create bucket schema
            bucket_data = schemas.BucketCreate(
                user_id=user_id_int,
                name=name,
                target_amount=target_amount_float,
                current_saved_amount=current_saved_amount_float,
                priority_score=priority_score_int,
                deadline=deadline,
                status=status
            )
            
            # Get database session
            db = next(get_db())
            
            # Create bucket using controller
            try:
                new_bucket = bucket_controller.create_bucket(db, bucket_data)
                
                # Convert model to dictionary for JSON serialization
                bucket_dict = {
                    "id": new_bucket.id,
                    "user_id": new_bucket.user_id,
                    "name": new_bucket.name,
                    "target_amount": new_bucket.target_amount,
                    "current_saved_amount": new_bucket.current_saved_amount,
                    "priority_score": new_bucket.priority_score,
                    "deadline": new_bucket.deadline.isoformat() if new_bucket.deadline else None,
                    "status": new_bucket.status
                }
                
                return json.dumps({
                    "success": True,
                    "message": f"Bucket '{name}' created successfully",
                    "data": bucket_dict
                })
                
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to create bucket: {str(e)}"
            })



#DELETING BUCKET -------------------------------------------------------


    @kernel_function(
        description="""Delete a bucket from the user.
        
        User will provide a name of the bucket to delete.
        
        Check if the bucket exists, you will have access to the list of buckets the user has from the frontend.
                            
        User requests to delete a bucket.
        
        If user does not specify the name of the bucket, simply ask for the name of the bucket to delete.
        
        Confirm if they want to delete the bucket
        """
        )
    async def delete_bucket(
        self,
        bucket_id: int,
        name: str
    ) -> str:
        """
        Delete a budget bucket for a user.
        """
        try:
            # Get database session
            db = next(get_db())       
            
            # Delete bucket using controller
            try:
                bucket_controller.delete_bucket(db, bucket_id)     
                return json.dumps({
                    "success": True,
                    "message": f"Bucket '{name}' deleted successfully",
                })
                
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to delete bucket: {str(e)}"
            })
            
            
#UPDATING BUCKET -------------------------------------------------------

    @kernel_function(
        description="""Update an existing bucket for the user.
        
        User can update any of the following bucket properties:
        - name
        - target amount
        - current saved amount
        - priority score (1-10)
        - deadline (parse natural language dates into YYYY-MM-DD)
        - status (active/completed/paused)
        
        Ask the user which bucket they want to update first, then ask which properties they want to change.
        Only ask about the specific properties they want to modify.
        
        Handle the conversation in a natural way - don't try to collect all properties at once.
        Parse amounts and dates from natural language descriptions.
        """
    )
    async def update_bucket(
        self,
        bucket_id: int,
        name: Optional[str] = None,
        target_amount: Optional[str] = None,
        current_saved_amount: Optional[str] = None,
        priority_score: Optional[str] = None,
        deadline: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """
        Update an existing budget bucket for a user.
        """
        try:
            # Parse parameters that were provided
            update_data = {}
            
            if name is not None:
                update_data["name"] = name
                
            if target_amount is not None:
                update_data["target_amount"] = float(target_amount)
                
            if current_saved_amount is not None:
                update_data["current_saved_amount"] = float(current_saved_amount)
                
            if priority_score is not None:
                update_data["priority_score"] = int(priority_score)
                
            if deadline is not None:
                update_data["deadline"] = deadline
                
            if status is not None:
                update_data["status"] = status
            
            # Create update schema
            bucket_update = schemas.BucketUpdate(**update_data)
            
            # Get database session
            db = next(get_db())
            
            # Update bucket using controller
            try:
                updated_bucket = bucket_controller.update_bucket(db, bucket_id, bucket_update)
                
                if not updated_bucket:
                    return json.dumps({
                        "success": False,
                        "error": f"Bucket with ID {bucket_id} not found"
                    })
                
                # Convert model to dictionary for JSON serialization
                bucket_dict = {
                    "id": updated_bucket.id,
                    "user_id": updated_bucket.user_id,
                    "name": updated_bucket.name,
                    "target_amount": updated_bucket.target_amount,
                    "current_saved_amount": updated_bucket.current_saved_amount,
                    "priority_score": updated_bucket.priority_score,
                    "deadline": updated_bucket.deadline.isoformat() if updated_bucket.deadline else None,
                    "status": updated_bucket.status
                }
                
                return json.dumps({
                    "success": True,
                    "message": f"Bucket updated successfully",
                    "data": bucket_dict
                })
                
            except ValueError as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to update bucket: {str(e)}"
            })