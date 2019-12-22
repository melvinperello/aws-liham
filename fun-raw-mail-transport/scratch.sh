# ------------------------------------------------------------------------------
# Local Variables for the Function.
# ------------------------------------------------------------------------------
export FUN_ENV="pr"
export FUN_CLEANUP="NONE"
export FUN_DOMAIN="codewizardsph.com"
export FUN_BUCKET="liham-store-codewizardsph.com-pr-zxcv"

# ------------------------------------------------------------------------------
# Liham Variables for User.
# ------------------------------------------------------------------------------
export LIHAM_BUCKET="liham-store-codewizardsph.com-pr-zxcv"
export LIHAM_DOMAIN="codewizardsph.com"
export LIHAM_USER="melvinperello"

# view all mails in inbox
aws s3api list-objects-v2 --bucket $LIHAM_BUCKET \
--prefix "store/$LIHAM_DOMAIN/$LIHAM_USER@$LIHAM_DOMAIN/inbox/" \
--output json \
--profile liham

# view all mails in inbox for December 22, 2019
aws s3api list-objects-v2 --bucket $LIHAM_BUCKET \
--prefix "store/$LIHAM_DOMAIN/$LIHAM_USER@$LIHAM_DOMAIN/inbox/2019/12/22/" \
--output json \
--profile liham

# view all mails in inbox for a specific time
aws s3api list-objects-v2 --bucket $LIHAM_BUCKET \
--prefix "store/$LIHAM_DOMAIN/$LIHAM_USER@$LIHAM_DOMAIN/inbox/<yyyy>/<MM>/<dd>/<HH>/<mm>/<ss>/" \
--output json \
--profile liham

# view mail
aws s3api get-object --bucket $LIHAM_BUCKET \
--key "store/codewizardsph.com/melvinperello@codewizardsph.com/inbox/2019/12/22/11/11/03/jhmvinperello-at-outlook.com.json" \
--profile liham \
mail.json

# delete mail
aws s3api delete-object --bucket $LIHAM_BUCKET \
--key "store/codewizardsph.com/melvinperello@codewizardsph.com/inbox/2019/12/22/07/35/55/riyuuhirain-at-gmail.com.json" \
--profile liham
