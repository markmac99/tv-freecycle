# s3 bucket used by email process

resource "aws_s3_bucket" "tv-freecycle" {
  force_destroy = false
  bucket        = "tv-freecycle"
  tags = {
    "billingtag" = "freecycle"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "tv_lifecycle_rule" {
  bucket = aws_s3_bucket.tv-freecycle.id
  rule {
    id     = "delete athena queries"
    status = "Enabled"
    noncurrent_version_expiration {
      noncurrent_days = 1
    }
    filter {
      prefix = "tmp/"
    }
    expiration {
      days                         = 1
      expired_object_delete_marker = false
    }
  }
  rule {
    id     = "delete old emails"
    status = "Enabled"

    expiration {
      days                         = 30
      expired_object_delete_marker = false
    }

    filter {
      prefix = "freecycle/"
    }

    noncurrent_version_expiration {
      noncurrent_days = 5
    }
  }
  rule {
    id     = "delete old mailbodies"
    status = "Enabled"

    expiration {
      days                         = 30
      expired_object_delete_marker = false
    }

    filter {
      prefix = "bodies/"
    }

    noncurrent_version_expiration {
      noncurrent_days = 5
    }
  }
}


resource "aws_s3_bucket" "tvf-att" {
  force_destroy = false
  bucket        = "tvf-att"
  tags = {
    "billingtag" = "freecycle"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "tvf_att_lifecycle_rule" {
  bucket = aws_s3_bucket.tvf-att.id
  rule {
    id     = "expire old files"
    status = "Enabled"
    expiration {
      days                         = 180
      expired_object_delete_marker = false
    }
  }
  rule {
    id     = "delete expired object"
    status = "Enabled"

    filter {
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

resource "aws_s3_bucket_acl" "tvf_att_acl"{
  bucket = aws_s3_bucket.tvf-att.id
  #acl    = "public-read"
}

resource "aws_s3_bucket_policy" "allow_website_access" {
  bucket = aws_s3_bucket.tvf-att.id
  policy = data.aws_iam_policy_document.websiteacesspolicy.json
}

data "aws_iam_policy_document" "websiteacesspolicy" {
  statement {
    actions = ["s3:GetObject"]
    sid     = "PublicReadGetObject"
    effect  = "Allow"
    principals { 
      type        = "AWS"
      identifiers = ["*"]
    }
    resources = ["${aws_s3_bucket.tvf-att.arn}/*"]
  }
}

