from pydantic import BaseModel


class CaseReviewRequest(BaseModel):
    case_id: int
    review_result: str
    review_remark: str
    operator_id: str = ""
