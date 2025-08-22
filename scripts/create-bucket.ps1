$suffix = -join ((1..8) | ForEach {Get-Random -input ([char[]]'abcdefghijklmnopqrstuvwxyz0123456789')})
$bucketName = "my-secure-bucket-$suffix"
$logsBucket = "access-logs-$suffix"

# Create main bucket
aws s3 mb s3://$bucketName

# Block public access
aws s3api put-public-access-block --bucket $bucketName --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Enable versioning
aws s3api put-bucket-versioning --bucket $bucketName --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption --bucket $bucketName --server-side-encryption-configuration '{\"Rules\":[{\"ApplyServerSideEncryptionByDefault\":{\"SSEAlgorithm\":\"AES256\"}}]}'

# Create logs bucket
aws s3 mb s3://$logsBucket
aws s3api put-public-access-block --bucket $logsBucket --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Enable logging
aws s3api put-bucket-logging --bucket $bucketName --bucket-logging-status '{\"LoggingEnabled\":{\"TargetBucket\":\"'$logsBucket'\",\"TargetPrefix\":\"access-logs/\"}}'

Write-Host "Bucket created: $bucketName"
Write-Host "Logs bucket: $logsBucket"