from typing import Optional

from pydantic import BaseModel


class DashboardQuery(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
