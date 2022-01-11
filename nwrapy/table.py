import os

class Table():
    """
    Class to allow the creation of CLI tables
    """

    def table(self, headers: list, data: list, col: str='|', rw: str='-', corner: str='+'):
        """
        """
        assert len(headers)==len(data)
        col_widths=self.column_width(headers, data)
        
        term_width=os.get_terminal_size().columns
        max_width=term_width/len(headers)
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
            string+=' '*rem
            rows[-1]+=string
        rows[-1]+=col

        rows.append('')
        for w in col_widths:
            rows[-1]+=corner+rw*(w-1)
        rows[-1]+=corner

        # Add data
        for i in range(len(data[0])):
            rows.append('')
            for j,da in enumerate(data):
                string=col+' '+da[i]
                rem=col_widths[j]-(len(string))
                string+=' '*rem
                rows[-1]+=string
            rows[-1]+=col

        rows.append('')
        for w in col_widths:
            rows[-1]+=corner+rw*(w-1)
        rows[-1]+=corner
        
        return rows
        
    def column_width(self, headers: list, data: list):
        """
        
        """
        lengths=[]

        for i in range(len(headers)):
            l=[len(headers[i])+3]
            for da in data[i]:
                l.append(len(da)+3)

            m=max(l)
            lengths.append(m)

        assert len(headers)==len(lengths)
        return lengths
