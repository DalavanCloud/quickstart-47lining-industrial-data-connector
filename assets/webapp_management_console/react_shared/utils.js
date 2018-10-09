import moment from 'moment'
import pluralize from 'pluralize'

const formatString = 'MM/DD/YYYY hh:mm A'

export function formatTimestamp(timestamp) {
    const momentObject = moment(timestamp);
    return momentObject.format(formatString);
}

export function getUtcDatetime() {
    return moment().utc().format(formatString);
}

export function formatDuration(minutes) {
    const hours = Math.floor(minutes/60);
    const minutesRemaining = minutes % 60;
    return `${hours > 0 ? `${hours} ${pluralize('hour', hours)}` : ''} ${minutesRemaining} ${pluralize('minute', minutesRemaining)}`
}
