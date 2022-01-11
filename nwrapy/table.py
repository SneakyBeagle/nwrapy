import os

class Table():

    def table(self, headers, data, col='|', rw='-', corner='+'):
        assert len(headers)==len(data)
        col_widths=self.column_width(headers, data)
        
        term_width=os.get_terminal_size().columns
        col_width=max(col_widths)
        row_div=corner+rw*(col_width-1)

        rows=['']
        for w in col_widths:
            rows[-1]+=corner+rw*(w-1)
        rows[-1]+=corner

        # Add headers
        rows.append('')
        for i,header in enumerate(headers):
            string=col+' '+header
            rem=col_widths[i]-(len(string))
            rows[-1]+=string+' '*rem
        rows[-1]+=col

        rows.append('')
        for w in col_widths:
            rows[-1]+=corner+rw*(w-1)
        rows[-1]+=corner

        # Add data
        for i in range(len(headers)):
            rows.append('')
            for j,da in enumerate(data):
                string=col+' '+da[i]
                rem=col_widths[j]-(len(string))
                rows[-1]+=string+' '*rem
            rows[-1]+=col

        rows.append('')
        for w in col_widths:
            rows[-1]+=corner+rw*(w-1)
        rows[-1]+=corner
        
        return rows
        
    def column_width(self, headers, data):
        lengths=[]

        for i in range(len(headers)):
            l=[len(headers[i])+3]
            for da in data[i]:
                l.append(len(da)+3)

            m=max(l)
            lengths.append(m)

        assert len(headers)==len(lengths)
        return lengths
