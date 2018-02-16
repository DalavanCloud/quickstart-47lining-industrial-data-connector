import moment from 'moment'


export function formatTimestamp(timestamp) {
    let momentObject = moment(timestamp);
    return momentObject.format('MM/DD/YYYY hh:mm A');
}
