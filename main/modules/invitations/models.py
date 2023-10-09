from main import db


class Invitation(db.Model):
    invitation_id = db.Column(db.Integer, primary_key=True)
    accepted = db.Column(db.Boolean)

    recipient_id = db.mapped_column(
        db.ForeignKey("account.account_id"), nullable=True
    )
    recipient = db.relationship("Account", back_populates="invitations")
