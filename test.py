def merge_intervals(intervals):
    if not intervals:
        return []

    # 1) Sort by start time
    intervals.sort(key=lambda x: x[0])

    merged = [intervals[0]]

    for start, end in intervals[1:]:
        last_start, last_end = merged[-1]

        # 2) Overlap if current start <= last end
        if start <= last_end:
            # Merge by extending the end if needed
            merged[-1][1] = max(last_end, end)
        else:
            merged.append([start, end])

    return merged

print(merge_intervals([[1,3],[2,6],[8,10],[15,18],[10,15]]))
# [[1,6],[8,10],[15,18]]