from main import db


list_account = db.Table(
    "list_account",
    db.Column("list_id", db.Integer, db.ForeignKey("list.list_id")),
    db.Column("account_id", db.Integer, db.ForeignKey("account.account_id"))
)


class List(db.Model):
    list_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False, default="")
    accounts = db.relationship("Account", secondary=list_account, back_populates="lists",
                               cascade='all,delete')

