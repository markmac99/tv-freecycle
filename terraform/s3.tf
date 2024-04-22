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

resource "aws_s3_bucket_acl" "tvf_att_acl" {
  bucket = aws_s3_bucket.tvf-att.id
  access_control_policy {
    grant {
      permission = "READ_ACP"
      grantee {
        type = "Group"
        uri  = "http://acs.amazonaws.com/groups/global/AllUsers"
      }
    }
    grant {
      permission = "READ"
      grantee {
        id   = "dccce3cf1b74e5e5993c35d6ff066f716bce2fbd04683d07c165d7fd0c28a9e4"
        type = "CanonicalUser"
      }
    }
    grant {
        permission = "READ_ACP"
        grantee {
          id   = "dccce3cf1b74e5e5993c35d6ff066f716bce2fbd04683d07c165d7fd0c28a9e4"
          type = "CanonicalUser"
        }
      }
    grant {
        permission = "WRITE"
        grantee {
          id   = "dccce3cf1b74e5e5993c35d6ff066f716bce2fbd04683d07c165d7fd0c28a9e4"
          type = "CanonicalUser"
        }
      }
    grant {
        permission = "WRITE_ACP"
        grantee {
          id   = "dccce3cf1b74e5e5993c35d6ff066f716bce2fbd04683d07c165d7fd0c28a9e4"
          type = "CanonicalUser"
        }
      }
    owner {
        id = "dccce3cf1b74e5e5993c35d6ff066f716bce2fbd04683d07c165d7fd0c28a9e4"
      }
  }
}

resource "aws_s3_bucket_policy" "allow_website_access" {
  bucket = aws_s3_bucket.tvf-att.id
  policy = jsonencode(
    {
      Statement = [
        {
          Action    = "s3:GetObject"
          Effect    = "Allow"
          Principal = {
            AWS = "*"
          }
          Resource  = "arn:aws:s3:::tvf-att/*"
          Sid       = "PublicReadGetObject"
        },
      ]
      Version   = "2012-10-17"
    }
  )
}

resource "aws_s3_bucket_policy" "allows_ses_access" {
  bucket = aws_s3_bucket.tv-freecycle.id
  policy = jsonencode(
    {
      Statement = [
      {
        Action    = "s3:PutObject"
        Condition = {
          StringEquals = {
            "aws:Referer" = "317976261112"
            }
        }
        Effect    = "Allow"
        Principal = {
          Service = "ses.amazonaws.com"
        }
        Resource  = "arn:aws:s3:::tv-freecycle/*"
        Sid       = "AllowSESPuts"
        },
      ]
    Version   = "2012-10-17"
    }
  )
}
