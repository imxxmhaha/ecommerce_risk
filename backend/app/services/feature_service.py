from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.blacklist import Blacklist
from app.models.risk_assessment import RiskAssessment
from app.models.risk_event import RiskEvent

ALLOWED_FEATURES = {
    "is_user_blacklisted", "is_order_blacklisted", "phone_related_user_count",
    "device_related_user_count", "is_ip_high_risk_area", "user_register_days",
    "user_refund_rate_90d", "user_complaint_count_90d", "user_high_risk_count_180d",
    "user_reject_count_180d", "order_amount", "order_item_count", "is_coupon_used",
    "coupon_discount_rate", "is_first_order", "user_order_count_1h", "user_cancel_count_7d",
    "user_after_sale_count_7d", "address_related_user_count", "address_order_count_1d",
    "is_address_ip_mismatch", "is_address_high_risk_area", "device_order_count_1h",
    "ip_order_count_1h", "logistics_complaint_count_30d", "payment_method",
}


class FeatureService:
    def build_features(self, db: Session, event: RiskEvent, payload: dict) -> dict:
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)
        half_year_ago = now - timedelta(days=180)

        phone = payload.get("phone")
        device_id = payload.get("device_id")
        ip = payload.get("ip")
        address = payload.get("address")

        features = {
            "is_user_blacklisted": self._active_match(db, "user_id", event.user_id),
            "is_order_blacklisted": self._active_match(db, "order_id", event.order_id),
            "phone_related_user_count": int(payload.get("phone_related_user_count", 1)),
            "device_related_user_count": int(payload.get("device_related_user_count", 1)),
            "is_ip_high_risk_area": bool(payload.get("is_ip_high_risk_area", False) or self._active_match(db, "ip", ip)),
            "user_register_days": int(payload.get("user_register_days", 30)),
            "user_refund_rate_90d": float(payload.get("user_refund_rate_90d", 0)),
            "user_complaint_count_90d": int(payload.get("user_complaint_count_90d", 0)),
            "user_high_risk_count_180d": self._high_risk_count(db, event.user_id, half_year_ago),
            "user_reject_count_180d": self._reject_count(db, event.user_id, half_year_ago),
            "order_amount": float(payload.get("order_amount", 0)),
            "order_item_count": int(payload.get("order_item_count", 1)),
            "is_coupon_used": bool(payload.get("is_coupon_used", False)),
            "coupon_discount_rate": float(payload.get("coupon_discount_rate", 0)),
            "is_first_order": self._is_first_order(db, event.user_id),
            "user_order_count_1h": self._event_count(db, event.user_id, one_hour_ago),
            "user_cancel_count_7d": int(payload.get("user_cancel_count_7d", 0)),
            "user_after_sale_count_7d": self._event_count(db, event.user_id, seven_days_ago, "after_sale_apply"),
            "address_related_user_count": int(payload.get("address_related_user_count", 1)),
            "address_order_count_1d": int(payload.get("address_order_count_1d", 0)),
            "is_address_ip_mismatch": bool(payload.get("is_address_ip_mismatch", False)),
            "is_address_high_risk_area": bool(payload.get("is_address_high_risk_area", False) or self._active_match(db, "address", address)),
            "device_order_count_1h": int(payload.get("device_order_count_1h", 0)),
            "ip_order_count_1h": int(payload.get("ip_order_count_1h", 0)),
            "logistics_complaint_count_30d": self._event_count(db, event.user_id, thirty_days_ago, "logistics_complaint"),
            "payment_method": payload.get("payment_method", "unknown"),
        }
        if phone and self._active_match(db, "phone", phone):
            features["phone_related_user_count"] = max(features["phone_related_user_count"], 4)
        if device_id and self._active_match(db, "device_id", device_id):
            features["device_related_user_count"] = max(features["device_related_user_count"], 6)
        return features

    def _active_match(self, db: Session, blacklist_type: str, blacklist_value) -> bool:
        if not blacklist_value:
            return False
        return db.query(Blacklist).filter(
            Blacklist.blacklist_type == blacklist_type,
            Blacklist.blacklist_value == str(blacklist_value),
            Blacklist.status == 1,
            Blacklist.deleted == 0,
        ).first() is not None

    def _event_count(self, db: Session, user_id: str, since, event_type: str = None) -> int:
        query = db.query(RiskEvent).filter(RiskEvent.user_id == user_id, RiskEvent.created_at >= since)
        if event_type:
            query = query.filter(RiskEvent.event_type == event_type)
        return query.count()

    def _is_first_order(self, db: Session, user_id: str) -> bool:
        return db.query(RiskEvent).filter(RiskEvent.user_id == user_id).count() <= 1

    def _high_risk_count(self, db: Session, user_id: str, since) -> int:
        return db.query(RiskAssessment).join(RiskEvent, RiskAssessment.event_id == RiskEvent.id).filter(
            RiskEvent.user_id == user_id,
            RiskAssessment.risk_level == "high",
            RiskAssessment.created_at >= since,
        ).count()

    def _reject_count(self, db: Session, user_id: str, since) -> int:
        return db.query(RiskAssessment).join(RiskEvent, RiskAssessment.event_id == RiskEvent.id).filter(
            RiskEvent.user_id == user_id,
            RiskAssessment.decision == "reject",
            RiskAssessment.created_at >= since,
        ).count()
