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

    @kernel_function(
        description="Create a new budget bucket for a user"
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
        """Create a new budget bucket for a user.
        
        Args:
            user_id: The ID of the user who owns this bucket
            name: The name of the bucket
            target_amount: The target amount to save in this bucket
            current_saved_amount: The current amount saved in this bucket
            priority_score: Priority score of the bucket (1-10)
            deadline: Deadline for the bucket in ISO format (YYYY-MM-DD)
            status: Status of the bucket (active, completed, etc.)
        """
        try:
            # Parse parameters
            user_id_int = int(user_id)
            target_amount_float = float(target_amount) if target_amount else 0.0
            current_saved_amount_float = float(current_saved_amount) if current_saved_amount else 0.0
            priority_score_int = int(priority_score) if priority_score else 1
            
            # Parse deadline if provided
            deadline_date = None
            if deadline:
                try:
                    deadline_date = datetime.fromisoformat(deadline)
                except ValueError:
                    return json.dumps({
                        "success": False,
                        "error": "Invalid deadline format. Please use YYYY-MM-DD format."
                    })
            
            # Create bucket schema
            bucket_data = schemas.BucketCreate(
                user_id=user_id_int,
                name=name,
                target_amount=target_amount_float,
                current_saved_amount=current_saved_amount_float,
                priority_score=priority_score_int,
                deadline=deadline_date,
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
