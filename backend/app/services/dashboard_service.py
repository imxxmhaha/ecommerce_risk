from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.risk_assessment import RiskAssessment
from app.models.risk_case import RiskCase
from app.models.risk_event import RiskEvent
from app.models.risk_rule import RiskRule
from app.models.rule_hit import RuleHit
from app.services.effective_risk_service import EffectiveRiskService


class DashboardService:
    def __init__(self):
        self.effective_risk_service = EffectiveRiskService()

    def dashboard(self, db: Session, start_date=None, end_date=None):
        start = self._parse(start_date) or (datetime.now() - timedelta(days=30))
        end = self._parse(end_date) or datetime.now()

        # 风险事件统计
        event_total = db.query(RiskEvent).filter(RiskEvent.created_at >= start, RiskEvent.created_at <= end).count()

        # 评估统计
        assessments = db.query(RiskAssessment).filter(RiskAssessment.created_at >= start, RiskAssessment.created_at <= end).all()
        effective_assessments = [self.effective_risk_service.effective_assessment(db, item) for item in assessments]
        high_count = sum(1 for a in effective_assessments if a["risk_level"] == "high")

        # 案件统计
        case_total = db.query(RiskCase).filter(RiskCase.created_at >= start, RiskCase.created_at <= end).count()
        resolved_case_total = db.query(RiskCase).filter(RiskCase.case_status.in_(["approved", "rejected"]), RiskCase.created_at >= start, RiskCase.created_at <= end).count()

        # 计算平均处理时长（小时）
        avg_case_process_hours = self._calc_avg_process_hours(db, start, end)

        # 风险等级分布
        dist = {}
        for item in effective_assessments:
            dist[item["risk_level"]] = dist.get(item["risk_level"], 0) + 1

        # 规则命中排行
        ranking_rows = (
            db.query(RiskRule.rule_name, RiskRule.rule_code, func.count(RuleHit.id))
            .join(RuleHit, RuleHit.rule_id == RiskRule.id)
            .filter(RuleHit.created_at >= start, RuleHit.created_at <= end, RiskRule.rule_status == 1)
            .group_by(RiskRule.rule_name, RiskRule.rule_code)
            .order_by(func.count(RuleHit.id).desc())
            .limit(10)
            .all()
        )

        # 风险事件趋势（按日聚合）
        risk_event_trend = self._calc_event_trend(db, start, end)

        return {
            "event_total": event_total,
            "high_risk_rate": round(high_count / len(effective_assessments), 4) if effective_assessments else 0,
            "case_total": case_total,
            "resolved_case_total": resolved_case_total,
            "avg_case_process_hours": avg_case_process_hours,
            "risk_level_distribution": [{"name": k, "value": v} for k, v in dist.items()],
            "rule_hit_ranking": [{"rule_name": n, "rule_code": c, "hit_count": count} for n, c, count in ranking_rows],
            "blacklist_hit_count": sum(count for _, c, count in ranking_rows if "BLACKLIST" in c),
            "risk_event_trend": risk_event_trend,
        }

    def _calc_avg_process_hours(self, db: Session, start: datetime, end: datetime) -> float:
        """计算案件平均处理时长（小时）"""
        # 查询已处理的案件（approved 或 rejected）
        resolved_cases = db.query(RiskCase).filter(
            RiskCase.case_status.in_(["approved", "rejected"]),
            RiskCase.created_at >= start,
            RiskCase.created_at <= end
        ).all()

        if not resolved_cases:
            return 0

        total_hours = 0
        count = 0
        for case in resolved_cases:
            # 使用 updated_at 作为处理完成时间
            if case.updated_at and case.created_at:
                delta = case.updated_at - case.created_at
                total_hours += delta.total_seconds() / 3600
                count += 1

        return round(total_hours / count, 1) if count > 0 else 0

    def _calc_event_trend(self, db: Session, start: datetime, end: datetime) -> list:
        """计算风险事件趋势（按日聚合）"""
        # 按日期分组统计事件数量
        trend_rows = (
            db.query(
                func.date(RiskEvent.created_at).label("date"),
                func.count(RiskEvent.id).label("count")
            )
            .filter(RiskEvent.created_at >= start, RiskEvent.created_at <= end)
            .group_by(func.date(RiskEvent.created_at))
            .order_by(func.date(RiskEvent.created_at))
            .all()
        )

        # 同时统计每日高风险事件数
        high_risk_rows = (
            db.query(
                func.date(RiskEvent.created_at).label("date"),
                func.count(RiskAssessment.id).label("count")
            )
            .join(RiskAssessment, RiskAssessment.event_id == RiskEvent.id)
            .filter(
                RiskEvent.created_at >= start,
                RiskEvent.created_at <= end,
                RiskAssessment.risk_level == "high"
            )
            .group_by(func.date(RiskEvent.created_at))
            .order_by(func.date(RiskEvent.created_at))
            .all()
        )

        high_risk_map = {str(row.date): row.count for row in high_risk_rows}

        return [
            {
                "date": str(row.date),
                "total": row.count,
                "high_risk": high_risk_map.get(str(row.date), 0)
            }
            for row in trend_rows
        ]

    def _parse(self, value):
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
