library(reshape2)

data <- read.csv("data.csv", stringsAsFactors = F)
data[is.na(data)] <- 0

data[, c(6:74)] <- as.data.frame(lapply(data[, c(6:74)], function(x) as.numeric(as.character(x))))

data$full_volume <- data$steel + data$copper + data$aluminum + data$unspecified_metal + 
                    data$wood + data$paper_cardboard + data$straw + data$concrete + 
                    data$cement + data$aggregates + data$brick + data$mortar_plaster + 
                    data$mineral_fill + data$plaster_board_gypsum + data$Adobe + 
                    data$Asphalt + data$Bitumen + data$natural_stone + data$cement_asbestos + 
                    data$Clay + data$siding_unspecified + data$Ceramics + data$Glass + 
                    data$Plastics + data$Polystyrene + data$PVC + data$Lineoleum + 
                    data$Carpet + data$Heraklith + data$Mineral_wool

refined.data <- data[, c(1:35,75)]

refined.data[, c(6:36)] <- refined.data[, c(6:36)] / refined.data$full_volume

aggregated.data <- aggregate(refined.data, by=list(refined.data$Country,refined.data$Region,refined.data$construction_period_end), FUN=mean, na.rm=TRUE)

# Remove and rename some columns
aggregated.data$id <- NULL
aggregated.data$Region <- NULL
aggregated.data$Country <- NULL
aggregated.data$construction_period_start <- NULL
aggregated.data$construction_period_end <- NULL

colnames(aggregated.data)[1] <- "Country"
colnames(aggregated.data)[2] <- "Region"
colnames(aggregated.data)[3] <- "Construction_end"

write.csv(aggregated.data, file = "aggregated_data.csv", row.names = F)
